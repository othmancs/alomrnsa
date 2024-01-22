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
from datetime import date, datetime

from odoo import tools
from odoo import api, fields, models


class EmployeeBroadFactor(models.Model):
    _name = "hr.employee.broad.factor"
    _description = "Employee Broadfactor"
    _auto = False

    name = fields.Char()
    no_of_occurrence = fields.Integer()
    no_of_days = fields.Integer()
    broad_factor = fields.Integer()

    def init(self):
        tools.drop_view_if_exists(self._cr, 'hr_employee_broad_factor')
        date_today = date.today()
        print("date_today", date_today)
        self._cr.execute("""
            create or replace view hr_employee_broad_factor as (
                select
                    e.id,
                    e.name, 
                    count(h.*) as no_of_occurrence,
                    sum(h.number_of_days) as no_of_days,
                    count(h.*)*count(h.*)*sum(h.number_of_days) as broad_factor
                from hr_employee e
                    full join (select * from hr_leave where state = 'validate' and date_to <= now()::timestamp) h
                    on e.id =h.employee_id
                group by e.id
               )""")


class ReportOverdue(models.AbstractModel):
    _name = 'report.ent_hrms_dashboard.report_broadfactor'

    @api.model
    def get_report_values(self, docids=None, data=None):
        sql = """select * from hr_employee_broad_factor"""
        self.env.cr.execute(sql)
        lines = self.env.cr.dictfetchall()
        return {
            'doc_model': 'hr.employee.broad_factor',
            'lines': lines,
            'Date': fields.date.today(),
        }
