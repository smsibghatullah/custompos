# -*- coding: utf-8 -*-
# from odoo import http


# class CustomPointOfSale(http.Controller):
#     @http.route('/custom_point_of_sale/custom_point_of_sale', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_point_of_sale/custom_point_of_sale/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_point_of_sale.listing', {
#             'root': '/custom_point_of_sale/custom_point_of_sale',
#             'objects': http.request.env['custom_point_of_sale.custom_point_of_sale'].search([]),
#         })

#     @http.route('/custom_point_of_sale/custom_point_of_sale/objects/<model("custom_point_of_sale.custom_point_of_sale"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_point_of_sale.object', {
#             'object': obj
#         })

