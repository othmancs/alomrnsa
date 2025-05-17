# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID

def create_contacts_for_existing_employees(cr, registry):
    """
    Post-init hook لإنشاء جهات اتصال للموظفين الموجودين
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    Employee = env['hr.employee']
    
    employees_without_partner = Employee.search([('partner_id', '=', False)])
    
    if employees_without_partner:
        # إنشاء جهات اتصال للموظفين الموجودين
        for employee in employees_without_partner:
            partner = env['res.partner'].create({
                'name': employee.name,
                'email': employee.work_email,
                'phone': employee.work_phone,
                'mobile': employee.mobile_phone,
                'company_id': employee.company_id.id,
                'type': 'contact',
                'active': True,
            })
            employee.write({'partner_id': partner.id})
