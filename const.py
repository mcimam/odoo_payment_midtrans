# Part of Odoo. See LICENSE file for full copyright and licensing details.

# The currencies supported by Flutterwave, in ISO 4217 format.
# See https://flutterwave.com/us/support/general/what-are-the-currencies-accepted-on-flutterwave.
# Last website update: June 2022.
# Last seen online: 24 November 2022.
SUPPORTED_CURRENCIES = [
    "IDR",
]


# Mapping of transaction states to Flutterwave payment statuses.
PAYMENT_STATUS_MAPPING = {
    "authorized": ["authorize"],
    "pending": ["pending"],
    "done": ["capture", "settlement"],
    "cancel": [
        "cancel",
        "refund",
        "partial_refund",
        "chargeback",
        "partial_chargeback",
    ],
    "error": ["failure", "deny", "expire    "],
}
