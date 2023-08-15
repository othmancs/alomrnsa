# -*- coding: utf-8 -*-
from odoo import api, fields, models

RELATIONS = [
    ('self', 'Self'),
    ('wife', 'Wife'),
    ('husband', 'Husband'),
    ('son', 'Son'),
    ('daughter', 'Daughter'),
    ('father', 'Father'),
    ('mother', 'Mother'),
    ('other', 'Other'),
]


class HrEmployeeIqama(models.Model):
    _name = 'hr.employee.iqama'
    _description = 'Employee Iqama Details'
    
    name = fields.Char(compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', ondelete="cascade")
    relation = fields.Selection(RELATIONS, string="Relation", required=True, default="self")
    iqama_number = fields.Char(string="Iqama No.", required=True)
    description = fields.Char(string="Description")
    expiry_date = fields.Date(string="Expiry Date")
    expiry_date_hijri = fields.Char(string="Expiry Date (Hijri)")
    issue_place = fields.Char(string="Place of Issue")
    state = fields.Selection([('valid', 'Valid'), ('invalid', 'Invalid')], string="Status", default="valid")

    _sql_constraints = [
        ('iqama_uniq', 'unique(employee_id, relation)', 'Already added Iqama !'),
    ]
    
    @api.depends('employee_id', 'iqama_number')
    def _compute_name(self):
        """For Search"""
        for iqama in self:
            iqama.name = "%s %s" % (iqama.employee_id.name, iqama.iqama_number)

    def open_edit_employee(self):
        self.ensure_one()

        return {
            'name': '%s %s' % (self.employee_id.name, dict(RELATIONS)[self.relation]),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.employee',
            'target': 'new',
            'res_id': self.employee_id.id,
            'views': [
                (self.env.ref('hr.view_employee_form').id, 'form'),
            ],
        }

