# # -*- coding: utf-8 -*-
# {
#     'name': "manage_reviews",
#
#     'summary': """
#         Short (1 phrase/line) summary of the module's purpose, used as
#         subtitle on modules listing or apps.openerp.com""",
#
#     'description': """
#         Long description of module's purpose
#     """,
#
#     'author': "My Company",
#     'website': "http://www.yourcompany.com",
#
#     # Categories can be used to filter modules in modules listing
#     # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
#     # for the full list
#     'category': 'Uncategorized',
#     'version': '0.1',
#
#     # any module necessary for this one to work correctly
#     'depends': ['base'],
#
#     # always loaded
#     'data': [
#         # 'security/ir.model.access.csv',
#         'views/views.xml',
#         'views/templates.xml',
#     ],
#     # only loaded in demonstration mode
#     'demo': [
#         'demo/demo.xml',
#     ],
# }

{
    'name': 'Quan Ly Danh Gia Nhan Su',
    'version': '1.0',
    'category': 'Uncategorized',
    'summary': 'Quan Ly Danh Gia Nhan Su',
    'description': "",
    'depends': ['base','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/manage_reviews_template.xml',
        'views/manage_reviews_evaluation.xml',
        'views/dashboard.xml',
        'views/web_custom_templates.xml',
        'views/reports.xml',
        'views/menu_views.xml',

    ],

    'assets': {
        'web.assets_qweb': [
            'manage_reviews/static/src/xml/*',
        ],
    },

    'application': True,
}
