
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

# Map payment method to snap payment method
PAYMENT_METHODS_MAPPING = {
    'bank_bca': 'bca_va',
    'bank_permata': 'permata_va',
    'bni': 'bni_va',
    'bsi': 'bsi_va',
    'cimb_niaga': 'cimb_va',
    'card': 'credit_card',
    'gopay': 'gopay',
    'credit_card': 'credit_card',
    'bank_transfer': 'bank_transfer',
    'qris': 'other_qris',

}


# Map transaction states to payment status.
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
