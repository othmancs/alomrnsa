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
from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    labour_card_number = fields.Char(string="Employee Card Number", size=14, required=True,
                                     help="Labour Card Number Of Employee")
    salary_card_number = fields.Char(string="Salary Card Number/Account Number", size=16, required=True,
                                     help="Salary card number or account number of employee")
    agent_id = fields.Many2one('res.bank', string="Agent/Bank", required=True, help="Agent ID or bank ID of Employee")

    def write(self, vals):
        if 'labour_card_number' in vals.keys():
            if len(vals['labour_card_number']) < 14:
                vals['labour_card_number'] = vals['labour_card_number'].zfill(14)
        if 'salary_card_number' in vals.keys():
            if len(vals['salary_card_number']) < 16:
                vals['salary_card_number'] = vals['salary_card_number'].zfill(16)
        return super(Employee, self).write(vals)

    @api.model
    def create(self, vals):
        if 'labour_card_number' in vals.keys():
            if len(vals['labour_card_number']) < 14:
                vals['labour_card_number'] = vals['labour_card_number'].zfill(14)
        if 'salary_card_number' in vals.keys():
            if len(vals['salary_card_number']) < 16:
                vals['salary_card_number'] = vals['salary_card_number'].zfill(16)
        return super(Employee, self).create(vals)


class Bank(models.Model):
    _inherit = 'res.bank'

    routing_code = fields.Char(string="Routing Code", size=9, required=True, help="Bank Route Code")

    def write(self, vals):
        if 'routing_code' in vals.keys():
            vals['routing_code'] = vals['routing_code'].zfill(9)
        return super(Bank, self).write(vals)

    @api.model
    def create(self, vals):
        vals['routing_code'] = vals['routing_code'].zfill(9)
        return super(Bank, self).create(vals)


class Company(models.Model):
    _inherit = 'res.company'

    employer_id = fields.Char(string="Employer ID", help="Company Employer ID")

    def write(self, vals):
        if 'company_registry' in vals:
            vals['company_registry'] = vals['company_registry'].zfill(13) if vals['company_registry'] else False
        if 'employer_id' in vals:
            vals['employer_id'] = vals['employer_id'].zfill(13) if vals['employer_id'] else False
        return super(Company, self).write(vals)

    @api.model
    def create(self, vals):
        vals['company_registry'] = vals['company_registry'].zfill(13) if vals['company_registry'] else False
        if 'employer_id' in vals:
            vals['employer_id'] = vals['employer_id'].zfill(13) if vals['employer_id'] else False
        return super(Company, self).create(vals)


