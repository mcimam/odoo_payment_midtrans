import logging


from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.payment import utils as payment_utils

from odoo.addons.ci_payment_midtrans.const import PAYMENT_STATUS_MAPPING, PAYMENT_METHODS_MAPPING

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    midtrans_token = fields.Char("Midtrans transaction token")

    def _get_specific_rendering_values(self, processing_values):
        """Override of payment to return Midtrans-specific rendering values.

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

        if self.payment_method_code != 'midtrans':
            param['enabled_payments'] = [PAYMENT_METHODS_MAPPING.get(self.payment_method_code, self.payment_method_code.lower())]

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

        reference = notification_data.get("order_id")
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

        self.provider_reference = f"midtrans-{self.reference}"

        payment_status = notification_data["transaction_status"]

        # determinse state
        if payment_status in PAYMENT_STATUS_MAPPING["pending"]:
            self._set_pending()
        elif payment_status in PAYMENT_STATUS_MAPPING["done"]:
            self._set_done()
        elif payment_status in PAYMENT_STATUS_MAPPING["cancel"]:
            self._set_canceled()
        elif payment_status in PAYMENT_STATUS_MAPPING["error"]:
            self._set_error(
                _(
                    "An error occurred during the processing of your payment (status %s). Please try "
                    "again.",
                    payment_status,
                )
            )
        else:
            _logger.warning(
                "Received data with invalid payment status (%s) for transaction with reference %s.",
                payment_status,
                self.reference,
            )
            self._set_error(
                "Midtrans: " + _("Unknown payment status: %s", payment_status)
            )

        self._set_pending()
