from odoo import models, fields


class BranchSalesComparison(models.TransientModel):
    _name = 'monetary.movement.wizard'
    _description = 'monetary_movement_wizard'

    date_start = fields.Date(string="تاريخ البدايه", required=True)
    date_end = fields.Date(string="تاريخ النهايه", required=True)
    branch_id = fields.Many2many('res.branch', string="الفرع", required=True)
    product_category_id = fields.Many2many('product.category', string="فئه المنج", limit=1, required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def get_clients_export_xlsx(self):
        return self.env.ref("sb_quantities_sold_report.report_quantities_sold").report_action(self)

    def generate_pdf_report(self):
        domain = [('invoice_date', '>=', self.date_start),
                  ('invoice_date', '<=', self.date_end),
                  ('state', '=', 'posted'),
                  ('move_type', '=', 'out_invoice'),
                  # ('line_ids.product_id.categ_id.id','=',obj.product_category_id.ids),
                  ('branch_id', '=', self.branch_id.ids)
                  ]
        lines_data = self.env['account.move'].search(domain)
        existing_branch = lines_data.mapped('branch_id')
        existing_products = list(set(lines_data.mapped('line_ids.product_id')))
        print('existing_branch', existing_branch)
        report_data = []

        branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in existing_branch]
        print('ssssssssssssss', branches)
        for branch in existing_branch:
            current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
            total_option1_branch = sum([sum(move.mapped('amount_untaxed')) for move in
                                        current_branch_lines.filtered(
                                            lambda x: x.payment_method == 'option1' and x.move_type != 'out_refund')])
            total_option2_branch = sum([sum(move.mapped('amount_untaxed')) for move in
                                        current_branch_lines.filtered(
                                            lambda x: x.payment_method == 'option2' and x.move_type != 'out_refund')])

            total_option1_branch_tax = sum([sum(move.mapped('amount_tax_signed')) for move in
                                            current_branch_lines.filtered(lambda
                                                                              x: x.payment_method == 'option1' and x.move_type != 'out_refund')])
            total_option2_branch_tax = sum([sum(move.mapped('amount_tax_signed')) for move in
                                            current_branch_lines.filtered(lambda
                                                                              x: x.payment_method == 'option2' and x.move_type != 'out_refund')])

            out_refund = self.env['account.move'].search([
                ('invoice_date', '>=', self.date_start),
                ('invoice_date', '<=', self.date_end),
                ('move_type', '=', 'out_refund'),
                ('branch_id', '=', branch.id),
                ('state', '=', 'posted')
            ])
            total_option1_out_refund = sum([sum(move.mapped('amount_untaxed')) for move in
                                            out_refund.filtered(lambda
                                                                    x: x.payment_method == 'option1')])
            total_option2_out_refund = sum([sum(move.mapped('amount_untaxed')) for move in
                                            out_refund.filtered(lambda
                                                                    x: x.payment_method == 'option2')])

            total_option1_tax_out_refund = abs(sum([sum(move.mapped('amount_tax_signed')) for move in
                                                    out_refund.filtered(lambda
                                                                            x: x.payment_method == 'option1')]))
            total_option2_tax_out_refund = abs(sum([sum(move.mapped('amount_tax_signed')) for move in
                                                    out_refund.filtered(lambda
                                                                            x: x.payment_method == 'option2')]))
   
            payments = self.env['account.payment'].search([
                ('branch_id', '=', branch.id),
                ('state', '=', 'posted'),
                ('date', '>=', self.date_start),
                ('date', '<=', self.date_end)
            ])
            total_payments_branch1 = sum(payment.amount_company_currency_signed for payment in payments if
                                         payment.payment_method_line_id.name == 'تحويل')
            total_payments_branch2 = sum(payment.amount_company_currency_signed for payment in payments if
                                         payment.payment_method_line_id.name == 'تحويل')
            total_payments_branch3 = sum(payment.amount_company_currency_signed for payment in payments if
                                         payment.payment_method_line_id.name == 'تحويل')
            total_payments_branch4 = sum(payment.amount_company_currency_signed for payment in payments if
                                         payment.payment_method_line_id.name == 'تحويل')
     
            total1 = abs(round(
                total_option1_branch + total_option1_branch_tax + total_option1_out_refund + total_option1_tax_out_refund,
                2))
            total2 = abs(round(
                total_option2_branch + total_option2_branch_tax + total_option2_out_refund + total_option2_tax_out_refund,
                2))
            print('sssssssssssssssssssssssss',total1)

            report_data_item = {
                 'branch_name': branch.name,
                 "total_option1_branch": total_option1_branch,
                 "total_option2_branch": total_option2_branch,
                 "total_option1_branch_tax": total_option1_branch_tax,
                 "total_option2_branch_tax": total_option2_branch_tax,
                 "total_option1_out_refund": total_option1_out_refund,
                 "total_option2_out_refund": total_option2_out_refund,
                 "total_option2_tax_out_refund": total_option2_tax_out_refund,
                 "total_option1_tax_out_refund": total_option1_tax_out_refund,
                 "total_payments_branch1": total_payments_branch1,
                 "total_payments_branch2": total_payments_branch2,
                 "total_payments_branch3": total_payments_branch3,
                 "total_payments_branch4": total_payments_branch4,
                 "total1": total1,
                 "total2": total2,
                 "total3": total_payments_branch1,
                 "total4": total_payments_branch2,
                 "total5": total_payments_branch3,
                 "total6": total_payments_branch4,
             }

            report_data.append(report_data_item)

        print('reeeeeeeeeeeee', report_data)
        data = {
            'form': self.read()[0],
            'data': report_data,
            'branches': branches,
        }
        return self.env.ref("sb_monetary_movement_report.monetary_movement_report").report_action(self, data=data)