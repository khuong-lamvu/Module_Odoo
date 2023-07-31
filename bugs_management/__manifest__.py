# # -*- coding: utf-8 -*-
# {
#     'name': "bugs_management",
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
    'name': 'Quan Ly Loi Du An',
    'version': '1.0',
    'category': 'Uncategorized',
    'summary': 'Quan Ly Loi Du An',
    'description': "",
    'depends': ['base','project','hr','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_error.xml',
        'views/bugs_view.xml',
        'views/save_bugs.xml',
        'views/process_view.xml',
        'views/dashboard_view.xml',
        'views/web_custom_templates.xml',
        'views/menu_view.xml',
    ],

    'assets': {
        'web.assets_qweb': [
            'bugs_management/static/src/xml/*.xml',
        ],
    },

    # 'application': True,
    # 'installable': True,
    # # 'application': True,
    # 'auto_install': False,
}