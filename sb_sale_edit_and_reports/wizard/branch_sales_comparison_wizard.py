from odoo import models, fields


class BranchSalesComparison(models.TransientModel):
    _name = 'branch.sales.comparison.wizard'
    _description = 'branch sales comparison wizard'

    date_start = fields.Date(string="تاريخ البدايه", required=True)
    date_end = fields.Date(string="تاريخ النهايه", required=True)
    product_category_id = fields.Many2one('product.category', string="فئه المنج", limit=1, required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def get_branch_export_xlsx(self):
        return self.env.ref("sb_sale_edit_and_reports.report_branch_sales_comparison").report_action(self)

    def generate_pdf_report(self):
        domain = [('date', '>=', self.date_start),
                  ('date', '<=', self.date_end),
                  ('state', '=', 'posted'),
                  ('move_type', '=', 'out_invoice')
                  ]
        product_category_id = self.product_category_id.id

        lines_data = self.env['account.move'].search(domain)
        line_data = lines_data.filtered(
            lambda x: any(line.product_id.categ_id.id == product_category_id for line in x.line_ids))
        existing_branch = line_data.mapped('branch_id')

        report_data = []
        for branch in existing_branch:
            current_branch_lines = line_data.filtered(lambda x: x.branch_id == branch)
            total_option1_branch = sum([sum(move.mapped('amount_untaxed')) for move in
                                        current_branch_lines.filtered(lambda x: x.payment_method == 'option1')])
            total_option2_branch = sum([sum(move.mapped('amount_untaxed')) for move in
                                        current_branch_lines.filtered(lambda x: x.payment_method == 'option2')])
            total_option1_branch_purchase = sum([sum(move.line_ids.mapped('purchase_price')) for move in
                                                 current_branch_lines.filtered(
                                                     lambda x: x.payment_method != 'option1')])
            total_option2_branch_purchase = sum([sum(move.line_ids.mapped('purchase_price')) for move in
                                                 current_branch_lines.filtered(
                                                     lambda x: x.payment_method != 'option2')])
            total_op1_op2_purchase = total_option1_branch_purchase + total_option2_branch_purchase
            total_op1_op2 = total_option1_branch + total_option2_branch

            out_refund_price = self.env['account.move'].search([
                ('move_type', '=', 'out_refund'),
                ('branch_id', '=', branch.id),
                ('state', '=', 'posted'),
                ('date', '>=', self.date_start),
                ('date', '<=', self.date_end)
            ])
            total_out_refund_price = sum(out_refund_price.mapped('amount_untaxed'))
            total_out_refund_purchase_price = sum(
                out_refund_price.line_ids.mapped(lambda x: x.purchase_price * x.quantity))

            total_all = abs(total_op1_op2) - abs(total_out_refund_price)
            profit = abs(total_all) - abs(total_out_refund_purchase_price)
            payments = self.env['account.payment'].search([
                ('branch_id', '=', branch.id),
                ('state', '=', 'posted'),
                ('date', '>=', self.date_start),
                ('date', '<=', self.date_end)
            ])
            total_payments_branch = sum(payments.mapped('amount_company_currency_signed'))
            total_purchase = abs(total_op1_op2_purchase) - abs(total_out_refund_purchase_price)

            wizard_data = self.read()[0]
            report_data_item = {
                'branch_name': branch.name,
                'total_option1': total_option1_branch,
                'total_option2': total_option2_branch,
                'total_op1_op2': total_op1_op2,
                'total_refund_price': total_out_refund_price,
                'total_all': total_all,
                'total_out_refund_cost_branch': total_purchase,
                'total_profit': profit,
                'total_payments': total_payments_branch,
            }
            report_data.append(report_data_item)
        data = {
            'form': wizard_data,
            'data': report_data
        }
        return self.env.ref("sb_sale_edit_and_reports.banch1_sales_comparison_report").report_action(self, data=data)
