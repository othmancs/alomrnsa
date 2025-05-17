# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID

def create_contacts_for_existing_employees(cr, registry):
    """Create contacts for all existing employees"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    employees = env['hr.employee'].search([('partner_id', '=', False)])
    
    for emp in employees:
        partner = env['res.partner'].create({
            'name': emp.name,
            'email': emp.work_email,
            'phone': emp.work_phone,
            'mobile': emp.mobile_phone,
            'company_id': emp.company_id.id,
            'type': 'contact'
        })
        emp.write({'partner_id': partner.id})
