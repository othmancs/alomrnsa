# -*- coding: utf-8 -*-
# from odoo import http


# class PoRefund(http.Controller):
#     @http.route('/po_refund/po_refund', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/po_refund/po_refund/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('po_refund.listing', {
#             'root': '/po_refund/po_refund',
#             'objects': http.request.env['po_refund.po_refund'].search([]),
#         })

#     @http.route('/po_refund/po_refund/objects/<model("po_refund.po_refund"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('po_refund.object', {
#             'object': obj
#         })
