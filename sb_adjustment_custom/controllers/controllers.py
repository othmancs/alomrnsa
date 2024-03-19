# -*- coding: utf-8 -*-
# from odoo import http


# class SbAdjustmentCustom(http.Controller):
#     @http.route('/sb_adjustment_custom/sb_adjustment_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sb_adjustment_custom/sb_adjustment_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sb_adjustment_custom.listing', {
#             'root': '/sb_adjustment_custom/sb_adjustment_custom',
#             'objects': http.request.env['sb_adjustment_custom.sb_adjustment_custom'].search([]),
#         })

#     @http.route('/sb_adjustment_custom/sb_adjustment_custom/objects/<model("sb_adjustment_custom.sb_adjustment_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sb_adjustment_custom.object', {
#             'object': obj
#         })
