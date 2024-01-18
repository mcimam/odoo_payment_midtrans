# -*- coding: utf-8 -*-

{
    "name": "Midtrans Payment Provider",
    "category": "Accounting",
    "summary": "Payment Provider: Midtrans",
    "version": "17.0.1.0.0",
    "description": "Unofficial module for Midtrans payment gateway.",
    "depends": ["payment"],
    "external_dependencies": {"python": ["midtransclient"]},
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    "data": [
        "views/payment_views.xml",
        "views/payment_midtrans_templates.xml",
        "data/payment_method_data.xml",
        "data/payment_provider_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "payment_midtrans/static/src/js/main.js",
        ],
    },
    "installable": True,
    "author": "Choirul Imam",
}
