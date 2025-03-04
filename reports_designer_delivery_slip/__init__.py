# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# def pre_init_check(cr):
#     from odoo import api, SUPERUSER_ID
#     from odoo.exceptions import Warning

#     # إزالة التحقق من إصدار Odoo
#     # من الممكن أن يظل التحقق من وجود الموديول الضروري كما هو
#     reports_designer = api.Environment(cr, SUPERUSER_ID, {})['ir.module.module'].search(
#         [('name', '=', 'reports_designer')]
#     )
    
#     if not reports_designer or reports_designer.state != "installed":
#         raise Warning('This Module requires the installed module "Report Designer (XLSX, XLSM)". Please install the module!')

#     if int(''.join([str(100+int(d)) for d in reports_designer.installed_version.split('.')[2:]])) < 101103131:
#         raise Warning(
#             'Module support "Report Designer (XLSX, XLSM)" module starting from Version 1.3.31, '
#             'found Version {}. Please update the module "Report Designer (XLSX, XLSM)".'
#             .format('.'.join(reports_designer.installed_version.split('.')[2:]))
#         )
#     return True
