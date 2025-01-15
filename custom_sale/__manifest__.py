# -*- coding: utf-8 -*-
{
    'name': "Custom Sale",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_line_view.xml',
        'views/menu_views.xml',
        'views/action_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

