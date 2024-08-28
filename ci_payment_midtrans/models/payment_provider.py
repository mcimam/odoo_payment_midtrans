# -*- coding: utf-8 -*-

import logging
import midtransclient

from odoo import api, fields, models, exceptions
from odoo.http import request

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

    def get_backend_endpoint(self):
        if self.state == "test":
            return "https://app.sandbox.midtrans.com/snap/v1/transactions"

        return "https://app.midtrans.com/snap/v1/transactions"

    def midtrans_form_generate_values(self, values):
        values["client_key"] = self.midtrans_client_key
        if self.state == "test":
            values["snap_js_url"] = "https://app.sandbox.midtrans.com/snap/snap.js"
        else:
            values["snap_js_url"] = "https://app.midtrans.com/snap/snap.js"

        if "return_url" not in values:
            values["return_url"] = "/"

        values["order"] = request.website.sale_get_order()

        amount = values["amount"]
        currency = values["currency"]

        # You must have currency IDR enabled
        currency_IDR = self.env["res.currency"].search([("name", "=", "IDR")], limit=1)

        assert currency_IDR.name == "IDR"

        # Convert to IDR
        if currency.id != currency_IDR.id:
            values["amount"] = int(round(currency.compute(amount, currency_IDR)))

            values["currency"] = currency_IDR
            values["currency_id"] = currency_IDR.id
        else:
            values["amount"] = int(round(amount))

        return values

    def _midtrans_make_transaction(self, param):
        """
        Make midtrans new transaction
        """
        snap = midtransclient.Snap(
            is_production=(self.state == "enabled"),
            server_key=self.midtrans_server_key,
            client_key=self.midtrans_client_key,
        )

        try:
            trx = snap.create_transaction(param)
        except midtransclient.MidtransAPIError as e:
            raise exceptions.UserError(e.message)

        return trx
