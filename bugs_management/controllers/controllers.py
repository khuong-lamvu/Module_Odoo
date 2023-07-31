# -*- coding: utf-8 -*-
# from odoo import http


# class BugsManagement(http.Controller):
#     @http.route('/bugs_management/bugs_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bugs_management/bugs_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bugs_management.listing', {
#             'root': '/bugs_management/bugs_management',
#             'objects': http.request.env['bugs_management.bugs_management'].search([]),
#         })

#     @http.route('/bugs_management/bugs_management/objects/<model("bugs_management.bugs_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bugs_management.object', {
#             'object': obj
#         })
