# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo import tools, _


class HREndServiceBenifitsType(models.Model):
    _name = 'hr.end.service.benefit.type'
    _description = 'Employee End Of Service Benefits types'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Type Name", required=True)
    deserved_after = fields.Float(string="Deserved After", required=True, )
    active = fields.Boolean(string="Active", default=True)
    type = fields.Selection(string="Type",
                            selection=[('replacement', 'Replacement'), ('ending_service', 'Ending Service'), ],
                            default='replacement', )
    zero_message = fields.Char(string="Message", default='This employee is not deserved reward')
    line_ids = fields.One2many(comodel_name="hr.end.service.benefit.type.line", inverse_name="type_id",
                               string="Calcualtions", required=False, )
    deletable = fields.Boolean(default=True)

    def unlink(self):
        for record in self:
            if record.deletable == False:
                raise ValidationError(_('You can not delete that type as it a predefine type'))
        res = super(HREndServiceBenifitsType, self).unlink()
        return res


class HREndServiceBenifitsTypeLine(models.Model):
    _name = 'hr.end.service.benefit.type.line'
    _description = 'Employee End Of Service Benefits types Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'

    @api.constrains('sequence')
    def _check_sequence(self):
        for record in self:
            if record.sequence:
                lines_count = self.env['hr.end.service.benefit.type.line'].search_count([
                    ('type_id', '=', record.type_id.id),
                    ('sequence', '=', record.sequence),
                    ('id', '!=', record.id),
                ])
                if lines_count > 0:
                    raise ValidationError('Lines Sequence Must Be Unique')

    sequence = fields.Integer(string="Sequence", required=False, )
    deserved_for = fields.Float(string="Deserved For First(Years)", required=True, )
    deserved_months = fields.Float(string="Deserved Months For Year", required=True, )
    type_id = fields.Many2one(comodel_name="hr.end.service.benefit.type", string="", required=False, )
    deletable = fields.Boolean(default=True)

    def unlink(self):
        for record in self:
            if record.deletable == False:
                raise ValidationError(_('You can not delete that line as it is belongs to predefine type'))
        res = super(HREndServiceBenifitsTypeLine, self).unlink()
        return res
