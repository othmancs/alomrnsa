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
from odoo import models, fields


class WizardReason(models.TransientModel):
    """
        Hr custody contract refuse wizard.
            """
    _name = 'wizard.reason'

    def send_reason(self):
        context = self._context
        reject_obj = self.env[context.get('model_id')].\
            search([('id', '=', context.get('reject_id'))])
        if 'renew' in context.keys():
            reject_obj.write({'state': 'approved',
                              'renew_reject': True,
                              'renew_rejected_reason': self.reason})
        else:
            if context.get('model_id') == 'hr.holidays':
                reject_obj.write({'rejected_reason': self.reason})
                reject_obj.action_refuse()
            else:
                reject_obj.write({'state': 'rejected',
                                  'rejected_reason': self.reason})

    reason = fields.Text(string="Reason", help="Reason")
