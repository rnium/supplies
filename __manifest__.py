# -*- coding: utf-8 -*-
{
    'name': "Supplies",

    'summary': "Manage RFPs and suppliers",

    'description': """
        This module is used to manage suppliers and RFPs.
    """,

    'author': "Md. Saiful Islam Roni",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'mail'],
    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/supplies_security.xml',
        'security/ir.model.access.csv',
        'wizard/supplies_rfp_report_wizard_views.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/email_templates.xml',
        'views/supplies_registration_views.xml',
        'views/supplies_rfp_views.xml',
        'views/supplies_menus.xml',
        'views/mail_blacklist_inherit.xml',
        'views/ir_sequence.xml',
        'views/res_bank_views.xml',
        'views/res_partner_views.xml',
        'views/res_partner_bank_views.xml',
        'views/purchase_order_views.xml',
        'views/portal_templates.xml',
        'report/supplies_rfp_templates.xml',
        'wizard/supplies_blacklist_wizard_view.xml',
        'wizard/supplies_reject_application_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'web/static/lib/jquery/jquery.js',
            'supplies/static/src/js/registration.js',
        ]
    }
}

