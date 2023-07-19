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
from datetime import datetime

from odoo import models, fields, api, _


class HrAnnouncements(models.Model):
    _inherit = 'hr.employee'

    def _announcement_count(self):
        now = datetime.now()
        now_date = now.date()
        for obj in self:
            announcement_ids_general = self.env['hr.announcement'].sudo().search([('is_announcement', '=', True),
                                                                                 ('state', 'in', ('approved', 'done')),
                                                                                  ('date_start', '<=', now_date)])
            announcement_ids_emp = self.env['hr.announcement'].sudo().search([('employee_ids', 'in', self.id),
                                                                              ('state', 'in', ('approved', 'done')),
                                                                              ('date_start', '<=', now_date)])
            announcement_ids_dep = self.env['hr.announcement'].sudo().search([('department_ids', 'in', self.department_id.id),
                                                                              ('state', 'in', ('approved', 'done')),
                                                                              ('date_start', '<=', now_date)])
            announcement_ids_job = self.env['hr.announcement'].sudo().search([('position_ids', 'in', self.job_id.id),
                                                                              ('state', 'in', ('approved', 'done')),
                                                                              ('date_start', '<=', now_date)])

            announcement_ids = announcement_ids_general.ids + announcement_ids_emp.ids + announcement_ids_dep.ids + announcement_ids_job.ids

            obj.announcement_count = len(set(announcement_ids))

    def announcement_view(self):
        now = datetime.now()
        now_date = now.date()
        for obj in self:

            announcement_ids_general = self.env['hr.announcement'].sudo().search([('is_announcement', '=', True),
                                                                                  ('state', 'in', ('approved', 'done')),
                                                                                  ('date_start', '<=', now_date)])
            announcement_ids_emp = self.env['hr.announcement'].sudo().search([('employee_ids', 'in', self.id),
                                                                              ('state', 'in', ('approved', 'done')),
                                                                              ('date_start', '<=', now_date)])
            announcement_ids_dep = self.env['hr.announcement'].sudo().search([('department_ids', 'in', self.department_id.id),
                                                                             ('state', 'in', ('approved', 'done')),
                                                                              ('date_start', '<=', now_date)])
            announcement_ids_job = self.env['hr.announcement'].sudo().search([('position_ids', 'in', self.job_id.id),
                                                                              ('state', 'in', ('approved', 'done')),
                                                                              ('date_start', '<=', now_date)])

            ann_obj = announcement_ids_general.ids + announcement_ids_emp.ids + announcement_ids_job.ids + announcement_ids_dep.ids

            ann_ids = []

            for each in ann_obj:
                ann_ids.append(each)
            view_id = self.env.ref('ent_hr_reward_warning.view_hr_announcement_form').id
            if ann_ids:
                if len(ann_ids) > 1:
                    for an_id in ann_ids:
                        value = {
                            'domain': str([('id', 'in', ann_ids)]),
                            'view_mode': 'tree,form',
                            'res_model': 'hr.announcement',
                            'view_id': False,
                            'type': 'ir.actions.act_window',
                            'name': _('Announcements'),
                            'res_id': an_id
                        }
                else:
                    value = {
                        'view_mode': 'form',
                        'res_model': 'hr.announcement',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Announcements'),
                        'res_id': ann_ids and ann_ids[0]
                    }
                return value

    announcement_count = fields.Integer(compute='_announcement_count', string='# Announcements', help="Count of Announcement's")