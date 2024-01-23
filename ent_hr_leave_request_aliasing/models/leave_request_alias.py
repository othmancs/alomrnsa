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
import re
from datetime import datetime, timedelta
from odoo import models, api
from odoo.tools import email_split


class HrLeaveAlias(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """This function extracts required fields of hr.holidays from
        incoming mail then creating records """
        try:
            if custom_values is None:
                custom_values = {}
            msg_subject = msg_dict.get('subject', '')
            subject = re.search('LEAVE REQUEST', msg_subject)
            if subject is not None:
                email_address = email_split(msg_dict.get('email_from', False))[
                    0]
                employee = self.env['hr.employee'].sudo().search([
                    '|',
                    ('work_email', 'ilike', email_address),
                    ('user_id.email', 'ilike', email_address)
                ], limit=1)
                msg_body = msg_dict.get('body', '')
                cleaner = re.compile('<.*?>')
                clean_msg_body = re.sub(cleaner, '', msg_body)
                date_list = re.findall(r'\d{2}/\d{2}/\d{4}', clean_msg_body)
                if len(date_list) > 0:
                    # date_from = date_list[0]
                    # if len(date_list) > 1:
                    if len(date_list) == 1:
                        start_date = datetime.strptime(date_list[0], '%d/%m/%Y')
                        date_to = start_date
                        # no_of_days_temp = 1
                    else:
                        start_date = datetime.strptime(date_list[0], '%d/%m/%Y')
                        date_to = datetime.strptime(date_list[1], '%d/%m/%Y')

                    no_of_days_temp = (datetime.strptime(str(date_to),
                                                         "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                        str(start_date), '%Y-%m-%d %H:%M:%S')).days

                    no_of_days_temp += 1
                    print(start_date, '111')
                    custom_values.update({
                        'name': msg_subject.strip(),
                        'employee_id': employee.id,
                        'holiday_status_id': 1,
                        'request_date_from': start_date,
                        'request_date_to': date_to,
                        'number_of_days': no_of_days_temp
                    })
            return super(HrLeaveAlias, self).message_new(msg_dict,
                                                         custom_values)
        except:
            pass
