# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class LeaveRuleLine(models.Model):
    _name = "hr.leave.rule.line"
    _description = "Leaves Rules Line"

    def compute_previous_line_id(self):
        for rec in self:
            rec.previous_line_id = False
            if rec.leave_type_id and rec.leave_type_id.rule_ids:
                previous_ids = rec.leave_type_id.rule_ids.filtered(lambda l: float(l.limit_from) < float(rec.limit_from) and float(l.limit_to) <= float(rec.limit_from))
                if previous_ids:
                    rec.previous_line_id = previous_ids.ids[-1]

    def compute_next_line_id(self):
        for rec in self:
            rec.next_line_id = False
            if rec.leave_type_id and rec.leave_type_id.rule_ids:
                previous_ids = rec.leave_type_id.rule_ids.filtered(lambda l: float(l.limit_from) >= float(rec.limit_to) and float(l.limit_to) > float(rec.limit_to))
                if previous_ids:
                    rec.next_line_id = previous_ids.ids[0]

    name = fields.Char(string="Name", required=True, copy=False)
    limit_from = fields.Integer(string="Limit From", required=True, copy=False)
    limit_to = fields.Integer(string="Limit To", copy=False)
    limit_per = fields.Integer(string="Limit(%)", required=True, copy=False)
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type", copy=False)
    previous_line_id = fields.Many2one('hr.leave.rule.line', string="Previous Line", compute="compute_previous_line_id")
    next_line_id = fields.Many2one('hr.leave.rule.line', string="Next Line", compute="compute_next_line_id")

    @api.constrains('limit_from', 'limit_to')
    def _check_days(self):
        for rule_id in self:
            if rule_id.limit_from > rule_id.limit_to:
                raise ValidationError(_("'Limit To' should be greater than 'Limit From'!"))
            line_ids = self.search([('limit_from', '<=', rule_id.limit_to),
                                    ('limit_to', '>', rule_id.limit_from),
                                    ('leave_type_id', '=', rule_id.leave_type_id.id),
                                    ('id', '<>', rule_id.id)])
            if line_ids:
                raise ValidationError(_('Two (2) Rule Lines for leave are overlapping!'))


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    is_deduction = fields.Boolean(string="Leave Deduction", default=False)
    skip = fields.Boolean('Allow to Skip', help="Allow to Skip Public Holidays", default=True)
    one_time_usable = fields.Boolean('One Time Used', default=False)
    is_annual_leave = fields.Boolean('Annual Leave', default=False)
    rule_ids = fields.One2many('hr.leave.rule.line', 'leave_type_id', string="Rules")
    deduction_by = fields.Selection([('day', 'Days'), ('year', 'Year'), ('hour', 'Hours')], string="Deduction By", default='hour')
    notes = fields.Text(string='Notes')

    
    @api.constrains('deduction_by', 'request_unit')
    def _check_deduction_by(self):
        for rec in self:
            if rec.deduction_by and (rec.request_unit != 'hour' and rec.deduction_by == 'hour') or (rec.request_unit == 'hour' and rec.deduction_by != 'hour'):
                raise ValidationError(_('Take Time Off in and Deduction By both must be hour type!!'))


    # @api.constrains('validity_start', 'validity_stop')
    # def _check_validity_date(self):
    #     for rec in self:
    #         if rec.validity_start and rec.validity_stop and rec.validity_start.year != rec.validity_stop.year:
    #             raise ValidationError(_('Leave type validity start and stop date must be from same year!!'))
