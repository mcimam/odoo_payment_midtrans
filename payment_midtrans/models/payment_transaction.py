import logging

from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    midtrans_token = fields.Char("Midtrans transaction token")

    def _get_specific_rendering_values(self, processing_values):
        """Override of payment to return Paypal-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != "midtrans":
            return res

        # base_url = self.provider_id.get_base_url()
        partner_first_name, partner_last_name = payment_utils.split_partner_name(
            self.partner_name
        )
        # webhook_url = urls.url_join(base_url, PaypalController._webhook_url)
        param = {
            "transaction_details": {
                "order_id": self.reference,
                "gross_amount": self.amount,
            },
            "credit_card": {"secure": True},
            "customer_details": {
                "first_name": partner_first_name,
                "last_name": partner_last_name,
                "email": self.partner_email,
                "phone": self.partner_phone,
            },
        }
        api_url = self.provider_id._midtrans_make_transaction(param)
        self.midtrans_token = api_url["token"]
        return {"api_url": api_url["redirect_url"]}

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Override of payment to find the transaction

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "midtrans" or len(tx) == 1:
            return tx

        reference = notification_data.get("tx_ref")
        if not reference:
            raise ValidationError(
                "Midtrans: " + _("Received data with missing reference.")
            )

        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "midtrans")]
        )
        if not tx:
            raise ValidationError(
                "Midtrans: "
                + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, notification_data):
        """Override of payment to process the transaction

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != "midtrans":
            return
