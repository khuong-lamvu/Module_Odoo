# -*- coding: utf-8 -*-
# from odoo import http


# class ManageReviews(http.Controller):
#     @http.route('/manage_reviews/manage_reviews/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/manage_reviews/manage_reviews/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('manage_reviews.listing', {
#             'root': '/manage_reviews/manage_reviews',
#             'objects': http.request.env['manage_reviews.manage_reviews'].search([]),
#         })

#     @http.route('/manage_reviews/manage_reviews/objects/<model("manage_reviews.manage_reviews"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('manage_reviews.object', {
#             'object': obj
#         })
