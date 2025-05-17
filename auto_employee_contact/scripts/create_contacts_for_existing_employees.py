# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

def create_contacts_for_existing_employees(cr, registry):
    """
    سكربت لمرة واحدة لإنشاء جهات اتصال لجميع الموظفين الموجودين.
    """
    env = api.Environment(cr, 1, {})
    Employee = env['hr.employee']
    Partner = env['res.partner']

    employees_without_partner = Employee.search([('partner_id', '=', False)])

    if not employees_without_partner:
        raise UserError(_("جميع الموظفين لديهم جهات اتصال مرتبطة بهم بالفعل!"))

    # إنشاء جهات اتصال للموظفين الموجودين (معالجة دفعات لتحسين الأداء)
    batch_size = 100  # عدد السجلات التي تتم معالجتها في كل دفعة
    for i in range(0, len(employees_without_partner), batch_size):
        batch = employees_without_partner[i:i + batch_size]
        for employee in batch:
            partner = Partner.create({
                'name': employee.name,
                'email': employee.work_email,
                'phone': employee.work_phone,
                'mobile': employee.mobile_phone,
                'company_id': employee.company_id.id,
                'type': 'contact',
                'active': True,
            })
            employee.write({'partner_id': partner.id})

    return True