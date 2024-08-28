# -*- coding: utf-8 -*-

import logging
import requests

from base64 import b64encode

from odoo import api, fields, models, exceptions
from odoo.addons.ci_payment_midtrans import const


_logger = logging.getLogger(__name__)


class AcquirerMidtrans(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(
        selection_add=[("midtrans", "Midtrans")], ondelete={"midtrans": "set default"}
    )

    # midtrans_method = fields.Selection(
    #     [("snap", "SNAP"), ("core", "Core API")], string="Midtrans Method"
    # )

    midtrans_merchant_id = fields.Char(
        "Midtrans Merchant ID",
        required_if_provider="midtrans",
        groups="base.group_user",
    )

    midtrans_client_key = fields.Char(
        "Midtrans Client Key", required_if_provider="midtrans", groups="base.group_user"
    )

    midtrans_server_key = fields.Char(
        "Midtrans Server Key", required_if_provider="midtrans", groups="base.group_user"
    )

    # === COMPUTE METHODS ===#
    @api.depends("code")
    def _compute_view_configuration_fields(self):
        """Override of payment to hide the credentials page.

        :return: None
        """
        super()._compute_view_configuration_fields()
        self.filtered(lambda p: p.code == "demo").show_credentials_page = False

    def _compute_feature_support_fields(self):
        """Override of `payment` to enable additional features."""
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == "midtrans").update(
            {
                "support_express_checkout": True,
                "support_manual_capture": False,
                "support_refund": False,
                "support_tokenization": False,
            }
        )

    # === BUSINESS METHODS ===#
    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == "midtrans":
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    def _get_default_payment_method_codes(self):
        """Override of `payment` to return the default payment method codes."""
        default_codes = super()._get_default_payment_method_codes()
        if self.code != "midtrans":
            return default_codes
        return const.DEFAULT_PAYMENT_METHODS_CODES

    # === MIDTRANS CALL METHODS ===#
    def _midtrans_endpoint(self):
        if self.state == "test":
            return "https://app.sandbox.midtrans.com/snap"

        return "https://app.midtrans.com/snap"

    def _midtrans_header(self):
        key = b64encode(f"{self.midtrans_server_key}:".encode()).decode()
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "basic %s" % key,
        }

    def _midtrans_handle_error(self, trx):
        sc = trx.status_code
        em = trx.json().get('error_messages')
        if sc == 401:
            raise exceptions.UserError("Midtrans Error: %s" % '. '.join(em))
        elif sc == 400:
            raise exceptions.UserError("Midtrans Error: %s" % '. '.join(em))
        elif sc == 500:
            raise exceptions.UserError("Midtrans Error: %s" % '. '.join(em))
        else:
            raise Exception("Midtrans Error: %s" % trx.body)

    def _midtrans_make_transaction(self, param):
        """
        Make midtrans new transaction
        """
        url = "/v1/transactions"
        url = self._midtrans_endpoint() + url

        trx = requests.post(
            url,
            json=param,
            headers=self._midtrans_header(),
        )

        if trx.status_code != 200:
            self._midtrans_handle_error(trx)

        res = trx.json()
        return res

    def _midtrans_make_refund(self, param):
        """
        Make refund 
        """
