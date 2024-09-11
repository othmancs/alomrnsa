# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime, timedelta, date, time
from odoo.tools.float_utils import float_round



class HREmployee(models.Model):
    _inherit = "hr.employee"

    current_year_allocation_count = fields.Float('Current Year Total number of days allocated.', compute='_compute_current_year_allocation_count')
    current_year_allocation_display = fields.Char(compute='_compute_current_year_allocation_count')
    current_year_remaining_leaves = fields.Float(
        compute='_compute_current_year_remaining_leaves', string='Current Year Remaining Paid Time Off',
        help='Current Year Total number of paid time off allocated to this employee, change this value to create allocation/time off request. '
             'Total based on all the time off types without overriding limit.')

    current_year_allocation_used_count = fields.Float('Current Year Total number of days off used', compute='_compute_current_year_total_allocation_used')
    current_year_allocation_used_display = fields.Char(compute='_compute_current_year_total_allocation_used')
    allocation_used_count = fields.Float('Total number of days off used', compute='_compute_total_allocation_used')
    allocation_used_display = fields.Char(compute='_compute_total_allocation_used')

    def _compute_total_allocation_used(self):
        for employee in self:
            employee.allocation_used_count = float_round(employee.allocation_count - employee.remaining_leaves, precision_digits=2)
            employee.allocation_used_display = "%g" % employee.allocation_used_count

    def _compute_current_year_allocation_count(self):
        year_start_date = date(date.today().year, 1, 1)
        year_end_date = date(date.today().year, 12, 31)

        data = self.env['hr.leave.allocation'].read_group([
            ('employee_id', 'in', self.ids),
            ('holiday_status_id.active', '=', True),
            ('state', '=', 'validate'),
            ('date_from', '>=', year_start_date),
            ('date_from', '<=', year_end_date)
        ], ['number_of_days:sum', 'employee_id'], ['employee_id'])
        rg_results = dict((d['employee_id'][0], {"employee_id_count": d['employee_id_count'], "number_of_days": d['number_of_days']}) for d in data)
        for employee in self:
            result = rg_results.get(employee.id)
            employee.current_year_allocation_count = float_round(result['number_of_days'], precision_digits=2) if result else 0.0
            employee.current_year_allocation_display = "%g" % employee.current_year_allocation_count
            # employee.allocations_count = result['employee_id_count'] if result else 0.0

    def _get_current_year_remaining_leaves(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        year_start_date = date(date.today().year, 1, 1)
        year_end_date = date(date.today().year, 12, 31)
        self._cr.execute("""
            SELECT
                sum(h.number_of_days) AS days,
                h.employee_id
            FROM
                (
                    SELECT holiday_status_id, number_of_days,
                        state, employee_id
                    FROM hr_leave_allocation
                    WHERE date_from >= %s AND date_from <= %s
                    UNION ALL
                    SELECT holiday_status_id, (number_of_days * -1) as number_of_days,
                        state, employee_id
                    FROM hr_leave
                ) h
                join hr_leave_type s ON (s.id=h.holiday_status_id)
            WHERE
                s.active = true AND h.state='validate' AND
                s.requires_allocation='yes' AND
                h.employee_id in %s
            GROUP BY h.employee_id""", (year_start_date, year_end_date, tuple(self.ids),))
        return dict((row['employee_id'], row['days']) for row in self._cr.dictfetchall())


    def _compute_current_year_remaining_leaves(self):
        remaining = {}
        if self.ids:
            remaining = self._get_current_year_remaining_leaves()
        for employee in self:
            value = float_round(remaining.get(employee.id, 0.0), precision_digits=2)
            # employee.leaves_count = value
            employee.current_year_remaining_leaves = value

    def _compute_current_year_total_allocation_used(self):
        for employee in self:
            employee.current_year_allocation_used_count = float_round(employee.current_year_allocation_count - employee.current_year_remaining_leaves, precision_digits=2)
            employee.current_year_allocation_used_display = "%g" % employee.current_year_allocation_used_count

    def check_leave_monthly(self):
        for rec in self.search([]):
            try:
                template_id = self.env.ref('saudi_hr_leaves_management.email_template_for_leave_monthly_reminder')
            except ValueError:
                template_id = False
            if template_id:
                hr_id = rec.hr_id or False
                if not hr_id:
                    hr = self.env['ir.config_parameter'].sudo().get_param('saudi_hr.hr_id')
                    hr_id = self.env['hr.employee'].browse(int(hr))
                template_id.with_context(hr_id=hr_id).send_mail(rec.id, force_send=True)


