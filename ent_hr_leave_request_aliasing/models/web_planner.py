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
#
# from odoo import api, models
#
#
# class PlannerHrLeave(models.Model):
#     """This class is used to activate web.planner feature in 'ent_hr_leave_request_aliasing' module"""
#
#     _inherit = 'web.planner'
#
#     @api.model
#     def _get_planner_application(self):
#         planner = super(PlannerHrLeave, self)._get_planner_application()
#         planner.append(['planner_hr_leave', 'Leave Planner'])
#         return planner
#
#     @api.model
#     def _prepare_planner_hr_leave_data(self):
#         alias_record = self.env.ref('ent_hr_leave_request_aliasing.mail_alias_leave')
#         return {
#             'alias_domain': alias_record.alias_domain,
#             'alias_name': alias_record.alias_name,
#         }
#
