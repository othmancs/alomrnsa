# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrWorkspaceExpense(http.Controller):
#     @http.route('/de_hr_workspace_expense/de_hr_workspace_expense', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_workspace_expense/de_hr_workspace_expense/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_workspace_expense.listing', {
#             'root': '/de_hr_workspace_expense/de_hr_workspace_expense',
#             'objects': http.request.env['de_hr_workspace_expense.de_hr_workspace_expense'].search([]),
#         })

#     @http.route('/de_hr_workspace_expense/de_hr_workspace_expense/objects/<model("de_hr_workspace_expense.de_hr_workspace_expense"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_workspace_expense.object', {
#             'object': obj
#         })
