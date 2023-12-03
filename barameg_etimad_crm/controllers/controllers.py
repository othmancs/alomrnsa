# -*- coding: utf-8 -*-
# from odoo import http


# class BaramegSaudiMonafasat(http.Controller):
#     @http.route('/barameg_saudi_monafasat/barameg_saudi_monafasat', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/barameg_saudi_monafasat/barameg_saudi_monafasat/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('barameg_etimad_crm.listing', {
#             'root': '/barameg_saudi_monafasat/barameg_saudi_monafasat',
#             'objects': http.request.env['barameg_etimad_crm.barameg_saudi_monafasat'].search([]),
#         })

#     @http.route('/barameg_saudi_monafasat/barameg_saudi_monafasat/objects/<model("barameg_etimad_crm.barameg_saudi_monafasat"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('barameg_etimad_crm.object', {
#             'object': obj
#         })
