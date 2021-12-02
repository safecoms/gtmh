# -*- coding: utf-8 -*-
{
    'name': "Purchase Approval",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Gam Hpang,gam.hpang@safecoms.com",
    'website': "https://safecoms.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/mail_data.xml',
        'wizard/purchase_refuse_reason_view.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/purchase_order_type_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
