# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrWorkspace(http.Controller):
#     @http.route('/de_hr_workspace/de_hr_workspace', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_workspace/de_hr_workspace/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_workspace.listing', {
#             'root': '/de_hr_workspace/de_hr_workspace',
#             'objects': http.request.env['de_hr_workspace.de_hr_workspace'].search([]),
#         })

#     @http.route('/de_hr_workspace/de_hr_workspace/objects/<model("de_hr_workspace.de_hr_workspace"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_workspace.object', {
#             'object': obj
#         })
