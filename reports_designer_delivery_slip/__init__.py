# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '12.0':
        raise Warning('Module support Odoo Version 12.0, found {}.'.format(server_serie))
    from odoo import api, SUPERUSER_ID
    reports_designer  = api.Environment(cr, SUPERUSER_ID, {})['ir.module.module'].search([('name', '=', 'reports_designer')])    
    if not len(reports_designer) or reports_designer.state != "installed":
        raise Warning('This Module requires the installed module "Report Designer (XLSX, XLSM)". Please install the module!')    
    if int(''.join([str(100+int(d)) for d in  reports_designer.installed_version.split('.')[2:]])) < 101103131:
        raise Warning('Module support "Report Designer (XLSX, XLSM)" module starting from Version 1.3.31, found Version {}. Please update the module "Report Designer (XLSX, XLSM)".'.format('.'.join(reports_designer.installed_version.split('.')[2:])))
    return True