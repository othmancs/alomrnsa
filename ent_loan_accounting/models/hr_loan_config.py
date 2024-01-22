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
from odoo import models, fields, api, _


class AccConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    loan_approve = fields.Boolean(default=False, string="Approval from Accounting Department",
                                  help="Loan Approval from account manager")

    @api.model
    def get_values(self):
        res = super(AccConfig, self).get_values()
        res.update(
            loan_approve=self.env['ir.config_parameter'].sudo().get_param('account.loan_approve')
        )
        print(res,'resssssss')
        return res

    
    def set_values(self):
        super(AccConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('account.loan_approve', self.loan_approve)

