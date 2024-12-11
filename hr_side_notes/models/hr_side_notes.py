# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrSideNotes(models.Model):
    _name = 'hr.side.notes'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Side notes"
    _rec_name = 'subject'

    def _get_default_type_id(self):
        return self.env["hr.side.notes.type"].search([], limit=1).id

    def _get_default_employee_id(self):
        emp_ids = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    type_id = fields.Many2one('hr.side.notes.type', string='Type', required=True, default=_get_default_type_id)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_get_default_employee_id, required=True)
    subject = fields.Char(required=True)
    notes = fields.Text()
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], default='0')
    state = fields.Selection(
        [('draft', 'Draft'), ('in progress', 'In Progress'), ('waiting', 'Waiting'), ('approved', 'Approved'),
         ('refused', 'Refused')],
        string='Status', default='draft')


class HrSideNotesType(models.Model):
    _name = 'hr.side.notes.type'

    name = fields.Char(translate=True, required=True)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_notes(self):
        for rec in self:
            rec.notes_count = self.env['hr.side.notes'].search_count([('employee_id', '=', rec.id)])

    notes_count = fields.Integer(string="Loan Count", compute='_compute_employee_notes')
