
SUPPORTED_CURRENCIES = [
    "IDR",
]

DEFAULT_PAYMENT_METHODS_CODES = [
    # Primary payment methods.
    'card',
    'dana',
    'shopeepay',
    'gopay',
    'ovo',
    'qris',

    # Brand payment methods.
    'visa',
    'mastercard',
]


# Mapping of transaction states to payment status.
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
    "error": ["failure", "deny", "expire"],
}
