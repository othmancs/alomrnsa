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

from odoo import api, fields, models


class HrLeaveConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    alias_prefix = fields.Char(string='Default Alias Name for Leave', help='Default Alias Name for Leave')
    alias_domain = fields.Char(string='Alias Domain', help='Default Alias Domain for Leave',
                               default=lambda self: self.env["ir.config_parameter"].get_param("mail.catchall.domain"))

    def set_values(self):
        super(HrLeaveConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].set_param
        set_param('alias_prefix', self.alias_prefix)
        set_param('alias_domain', self.alias_domain ),


    @api.model
    def get_values(self):
        res = super(HrLeaveConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            alias_prefix=get_param('alias_prefix', default=''),
            alias_domain=get_param('alias_domain', default=''),
        )
        return res

