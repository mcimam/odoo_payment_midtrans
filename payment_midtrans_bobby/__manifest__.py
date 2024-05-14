# -*- coding: utf-8 -*-

{
    "name": "Midtrans Payment Provider",
    "category": "Accounting",
    "summary": "Payment Provider: Midtrans",
    "version": "16.0.0.1",
    "description": """
        Unofficial module for Midtrans payment gateway.
    """,
    "depends": ["payment", "l10n_id"],
    "external_dependencies": {"python": ["midtransclient"]},
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "data": [
        "views/payment_views.xml",
        "views/payment_midtrans_templates.xml",
        "data/payment_provider_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "payment_midtrans_bobby/static/src/js/main.js",
        ],
    },
    "installable": True,
    "author": "Choirul Imam",
    "website": "http://dozy.moe",
}
