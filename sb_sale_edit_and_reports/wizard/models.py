from odoo import models, fields, api


class SalesReportWizard(models.TransientModel):
    _name = 'sales.report.wizard'
    _description = 'sales report wizard'

    date_start = fields.Date(string="تاريخ البدايه", required=True)
    date_end = fields.Date(string="تاريخ النهايه", required=True)
    branch_ids = fields.Many2many('res.branch', string="الفرع")
    payment_type = fields.Selection([
        ('all', 'الكل'),
        ('cash', 'نقدي'),
        ('credit', 'آجل')
    ], string="نوع الدفع", default='all')
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def get_sales_export_xlsx(self):
        return self.env.ref("sb_sale_edit_and_reports.report_sales_report").report_action(self)

    def generate_pdf_report(self):
        domain = [('invoice_date', '>=', self.date_start),
                  ('invoice_date', '<=', self.date_end),
                  ('move_type', '=', 'out_invoice'),
                  ('state', '=', 'posted')
                  ]

        # Filter by branch if selected
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))

        # Filter by payment type if not 'all'
        if self.payment_type != 'all':
            if self.payment_type == 'cash':
                domain.append(('payment_method', '=', 'option1'))
            elif self.payment_type == 'credit':
                domain.append(('payment_method', '=', 'option2'))

        lines_data = self.env['account.move'].search(domain)
        existing_branches = lines_data.mapped('branch_id')
        report_data = []
        branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in existing_branches]

        for branch in existing_branches:
            current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
            total_out_refund_purchase_price = 0.0
            total_out_refund_price = 0.0

            for line in current_branch_lines:
                out_refund_price = self.env['account.move'].search([
                    ('move_type', '=', 'out_refund'),
                    ('branch_id', '=', branch.id),
                    ('reversed_entry_id', '=', line.id),
                    ('state', '=', 'posted')
                ])
                total_out_refund_price += sum(out_refund_price.line_ids.mapped(lambda x: x.price_unit * x.quantity))
                total_out_refund_purchase_price += sum(
                    out_refund_price.line_ids.mapped(lambda x: x.purchase_price * x.quantity))

            for account in current_branch_lines:
                invoice_number = account.name
                seller_name = account.created_by_id.name
                customer_name = account.partner_id.name
                invoice_date = account.invoice_date
                state = account.payment_state
                cost = sum(account.line_ids.mapped(lambda line: line.purchase_price * line.quantity))
                payment_method = account.payment_method
                price = sum(account.mapped('amount_untaxed'))
                total_discount = sum(account.line_ids.mapped('discount'))
                net_cost = sum(account.line_ids.mapped(lambda line: (line.price_unit * line.quantity) - line.discount))

                if payment_method == 'option1':
                    payment_method = 'نقدى'
                elif payment_method == 'option2':
                    payment_method = 'اجل'
                else:
                    payment_method = '-'

                out_refund = self.env['account.move'].search([
                    ('move_type', '=', 'out_refund'),
                    ('branch_id', '=', branch.id),
                    ('reversed_entry_id', '=', account.id),
                    ('state', '=', 'posted')
                ])

                out_refund_purchase_price = 0.0
                out_refund_price = 0.0
                for ac in out_refund:
                    out_refund_purchase_price += sum(ac.line_ids.mapped(lambda x: x.purchase_price * x.quantity))
                    out_refund_price += sum(ac.mapped('amount_untaxed'))

                report_data_item = {
                    'branch_name': branch.name,
                    'invoice_number': invoice_number,
                    'seller_name': seller_name,
                    'customer_name': customer_name,
                    'payment_method': payment_method,
                    'invoice_date': invoice_date,
                    'total_price': price,
                    'total_discount': total_discount,
                    'net_cost': net_cost,
                    'cost': cost,
                    'total_credit_note': out_refund_price,
                    't': out_refund_purchase_price,
                    'state': state
                }

                report_data.append(report_data_item)

        data = {
            'form': self.read()[0],
            'data': report_data,
            'branches': branches,
        }
        return self.env.ref("sb_sale_edit_and_reports.sales_report").report_action(self, data=data)
