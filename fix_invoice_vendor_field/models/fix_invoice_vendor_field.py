from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_vendor_bill_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        store=True,
    )

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_vendor_bill_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        store=True,
    )

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    invoice_vendor_bill_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        store=True,
    )
