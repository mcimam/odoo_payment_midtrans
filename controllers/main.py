from hashlib import sha512
import logging

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


def _prune_dict(data):
    if isinstance(data, dict):
        return {
            key: _prune_dict(value) for key, value in data.items() if value is not None
        }

    return data


class MidtransController(http.Controller):
    _return_url = "/payment/midtrans/return"
    _webhook_url = "/payment/midtrans/webhook"

    @http.route(_return_url, type="http", methods=["GET"], auth="public")
    def midtrans_return_checkout(self, **data):
        """Process return from midtrans web after checkout
        :param dict data: Notification Data
        """
        _logger.info("Handling redirection from mmidtrans web checkout")

        request.env["payment.transaction"].sudo()._handle_notification_data("midtrans", data)
        return request.redirect("/payment/status")

    @http.route(_webhook_url, type="json", methods=["POST"], auth="public")
    def midtrans_hook_notif(self, **data):
        """Process notification from midtarns web
        :param dict data: Notification data
        """
        data = request.get_json_data()

        _logger.info("Handling notification from mmidtrans web checkout")
        _logger.debug(data)

        try:
            tx = request.env["payment.transaction"].sudo()._get_tx_from_notification_data("midtrans", data)
            self._verify_midtrans_signature(data, tx)

            request.env["payment.transaction"].sudo()._handle_notification_data("midtrans", data)
        except ValidationError:  # Acknowledge the notification to avoid getting spammed.
            _logger.exception("Unable to handle the notification data; skipping to acknowledge")

        return request.make_json_response("")

    @staticmethod
    def _verify_midtrans_signature(data, tx):
        """Check if signature match
        :param data : recieved notification data
        :param recordset: transaction data

        """
        # Security check

        provider = tx.provider_id
        signature_data = (
            data["order_id"]
            + data["status_code"]
            + data["gross_amount"]
            + provider.midtrans_server_key
        )

        assert (data["signature_key"] == sha512(signature_data.encode("UTF-8")).hexdigest())
