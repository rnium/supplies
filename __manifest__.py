# -*- coding: utf-8 -*-
{
    'name': "BJIT Supplies",

    'summary': "Manage suppliers and RFPs for BJIT",

    'description': """
        This module is used to manage suppliers and RFPs for BJIT.
    """,

    'author': "Md. Saiful Islam Roni",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'web/static/lib/jquery/jquery.js',
            'bjit_supplies/static/src/js/registration.js',
        ]
    }
}

