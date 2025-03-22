from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    # Adding the missing field
    schedule_pay = fields.Char(string='Schedule Pay', help="Payment schedule for the contract")
