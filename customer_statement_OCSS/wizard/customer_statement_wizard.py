from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CustomerStatementWizard(models.TransientModel):
    _name = 'customer.statement.wizard'
    _description = 'Customer Statement Wizard'

    partner_id = fields.Many2one(
        'res.partner', 
        string='Customer', 
        required=True,
        domain=[('customer_rank', '>', 0)]  # تأكد أن العميل لديه رتبة عميل
    )
    date_from = fields.Date(
        string='From Date', 
        required=True,
        default=lambda self: fields.Date.context_today(self)
    )
    date_to = fields.Date(
        string='To Date', 
        required=True,
        default=lambda self: fields.Date.context_today(self)
    )
    branch_id = fields.Many2one(
        'multi.branch', 
        string='Branch',
        domain="[('company_id', '=', company_id)]" if 'multi_branch_base' in self.env else []
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """تأكد من أن العميل صالح وقم بإعادة تعيين الفرع إذا لزم الأمر"""
        if not self.partner_id or not self.partner_id.id:
            self.branch_id = False
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("Please select a valid customer")
                }
            }
        
        if isinstance(self.partner_id.id, models.NewId):
            raise UserError(_("Please save the customer before generating the statement"))

    def action_print_report(self):
        self.ensure_one()
        # التحقق من صحة البيانات قبل المتابعة
        if not isinstance(self.partner_id.id, int):
            raise UserError(_("Invalid customer selected"))
        
        if self.date_from > self.date_to:
            raise UserError(_("End date must be greater than start date"))

        data = {
            'form_data': {
                'partner_id': self.partner_id.id,
                'partner_name': self.partner_id.name,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'branch_id': self.branch_id.id if self.branch_id else False,
                'branch_name': self.branch_id.name if self.branch_id else '',
                'company_id': self.company_id.id,
            }
        }
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'customer_statement_OCSS.customer_statement_report',
            'report_type': 'qweb-pdf',
            'data': data,
            'context': self.env.context
        }
