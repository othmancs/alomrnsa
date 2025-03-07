# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

import datetime
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

date_format = "%Y-%m-%d"
RESIGNATION_TYPE = [('resigned', 'Normal Resignation'),
                    ('fired', 'Fired by the company')]

class HrResignation(models.Model):
    _name = 'hr.resignation'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee", default=lambda self: self.env.user.employee_id.id,
                                  help='Name of the employee for whom the request is creating')
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id',
                                    help='Department of the employee')
    resign_confirm_date = fields.Date(string="Confirmed Date",
                                      help='Date on which the request is confirmed by the employee.',
                                      track_visibility="always")
    approved_revealing_date = fields.Date(string="Approved Last Day Of Employee",
                                          help='Date on which the request is confirmed by the manager.',
                                          track_visibility="always")
    joined_date = fields.Date(string="Join Date", store=True,
                              help='Joining date of the employee.i.e Start date of the first contract')

    expected_revealing_date = fields.Date(string="Last Day of Employee", required=True,
                                          help='Employee requested date on which he is revealing from the company.')
    reason = fields.Text(string="Reason", required=True, help='Specify reason for leaving the company')
    notice_period = fields.Char(string="Notice Period")
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('approved', 'Approved'), ('cancel', 'Rejected')],
        string='Status', default='draft', track_visibility="always")
    resignation_type = fields.Selection(selection=RESIGNATION_TYPE, help="Select the type of resignation: normal "
                                                                         "resignation or fired by the company")
    read_only = fields.Boolean(string="check field")
    employee_contract = fields.Char(String="Contract")

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def _compute_read_only(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_user'):
            self.read_only = True
        else:
            self.read_only = False

    @api.onchange('employee_id')
    def set_join_date(self):
        self.joined_date = self.employee_id.joining_date

    @api.model
    def create(self, vals):
        # assigning the sequence for the record
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.resignation') or _('New')
        res = super(HrResignation, self).create(vals)
        return res

    @api.constrains('employee_id')
    def check_employee(self):
        # Checking whether the user is creating leave request of his/her own
        for rec in self:
            if not self.env.user.has_group('hr.group_hr_user'):
                if rec.employee_id.user_id.id and rec.employee_id.user_id.id != self.env.uid:
                    raise ValidationError(_('You cannot create request for other employees'))

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def check_request_existence(self):
        # Check whether any resignation request already exists
        for rec in self:
            if rec.employee_id:
                resignation_request = self.env['hr.resignation'].search([('employee_id', '=', rec.employee_id.id),
                                                                         ('state', 'in', ['confirm', 'approved'])])
                if resignation_request:
                    raise ValidationError(_('There is a resignation request in confirmed or'
                                            ' approved state for this employee'))
                if rec.employee_id:
                    no_of_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
                    for contracts in no_of_contract:
                        if contracts.state == 'open':
                            rec.employee_contract = contracts.name
                            rec.notice_period = contracts.notice_days

    @api.constrains('joined_date')
    def _check_dates(self):
        # validating the entered dates
        for rec in self:
            resignation_request = self.env['hr.resignation'].search([('employee_id', '=', rec.employee_id.id),
                                                                     ('state', 'in', ['confirm', 'approved'])])
            if resignation_request:
                raise ValidationError(_('There is a resignation request in confirmed or'
                                        ' approved state for this employee'))

    def confirm_resignation(self):
        if self.joined_date:
            if self.joined_date >= self.expected_revealing_date:
                raise ValidationError(_('Last date of the Employee must be anterior to Joining date'))
            for rec in self:
                rec.state = 'confirm'
                rec.resign_confirm_date = str(datetime.now())
        else:
            raise ValidationError(_('Please set joining date for employee'))

    def cancel_resignation(self):
        for rec in self:
            rec.state = 'cancel'

    def reject_resignation(self):
        for rec in self:
            rec.state = 'cancel'

    def reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.employee_id.active = True
            rec.employee_id.resigned = False
            rec.employee_id.fired = False

    def approve_resignation(self):
        for rec in self:
            if rec.expected_revealing_date and rec.resign_confirm_date:
                no_of_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
                for contracts in no_of_contract:
                    if contracts.state == 'open':
                        rec.employee_contract = contracts.name
                        rec.state = 'approved'
                        rec.approved_revealing_date = rec.resign_confirm_date + timedelta(days=contracts.notice_days)
                    else:
                        rec.approved_revealing_date = rec.expected_revealing_date

                # التحقق من القروض/المعدات قبل الموافقة على الاستقالة
                loans = self.env['hr.employee.loan'].search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'loaned')])
                if not loans:
                    # إذا لم يكن هناك قروض أو معدات نشطة، نقوم بإنهاء عقد الموظف
                    rec.employee_id.active = False
                    rec.employee_id.resign_date = rec.expected_revealing_date
                    if rec.resignation_type == 'resigned':
                        rec.employee_id.resigned = True
                    else:
                        rec.employee_id.fired = True
                    
                    # تعطيل حساب الموظف إذا كان موجودًا
                    if rec.employee_id.user_id:
                        rec.employee_id.user_id.active = False
                        rec.employee_id.user_id = None
                else:
                    raise ValidationError(_('لا يمكن للموظف الاستقالة لأنه لا يزال لديه قروض أو معدات نشطة.'))
            else:
                raise ValidationError(_('يرجى إدخال تواريخ صحيحة.'))

    def update_employee_status(self):
        resignation = self.env['hr.resignation'].search([('state', '=', 'approved')])
        for rec in resignation:
            if rec.expected_revealing_date <= fields.Date.today() and rec.employee_id.active:
                # التحقق من القروض/المعدات قبل إنهاء العقد
                loans = self.env['hr.employee.loan'].search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'loaned')])
                if not loans:
                    rec.employee_id.active = False
                    rec.employee_id.resign_date = rec.expected_revealing_date
                    if rec.resignation_type == 'resigned':
                        rec.employee_id.resigned = True
                    else:
                        rec.employee_id.fired = True
                    
                    # تعطيل حساب الموظف إذا كان موجودًا
                    if rec.employee_id.user_id:
                        rec.employee_id.user_id.active = False
                        rec.employee_id.user_id = None
                else:
                    raise ValidationError(_('لا يمكن للموظف أن يتم تصنيفه كمستقيل لأنه لا يزال لديه قروض أو معدات نشطة.'))
