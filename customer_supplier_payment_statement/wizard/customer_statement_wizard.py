from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CustomerReportWizard(models.TransientModel):
    _name = 'customer.vendor.wizard'

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(required=True, default=lambda self: fields.Date.context_today(self), string="End Date")
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True,  change_default=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def check_date_range(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('End Date should be greater than Start Date.'))

    def print_pdf(self):
        date_from = self.date_from
        date_to = self.date_to
        self.check_date_range()
        datas = {
            'start_date': date_from,
            'end_date': date_to,
            'partner_id': self.partner_id.id

        }
        return self.env.ref('customer_vendor_statement.action_customer_template').report_action(self, data=datas)

    def print_xlsx(self):
        self.check_date_range()
        date_from = self.date_from
        date_to = self.date_to
        datas = {
            'id': self.id,
            'start_date': date_from,
            'end_date': date_to,
        }
        return self.env.ref('customer_vendor_statement.action_customer_vendor_xlsx').report_action(self, data=datas)
