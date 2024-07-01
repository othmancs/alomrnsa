from odoo import models, fields, api


class SalesReportWizard(models.TransientModel):
    _name = 'sales.report.wizard'
    _description = 'sales report wizard'

    date_start = fields.Date(string="تاريخ البدايه", required=True)
    date_end = fields.Date(string="تاريخ النهايه", required=True)
    branch_ids = fields.Many2many('res.branch', string="الفرع")
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def get_sales_export_xlsx(self):
        return self.env.ref("sb_sale_edit_and_reports.report_sales_report").report_action(self)

    # def generate_pdf_report(self):
    #     domain = [('date', '>=', self.date_start),
    #               ('date', '<=', self.date_end)]
    #     if self.branch_ids:
    #         domain.append(('branch_id', 'in', self.branch_ids.ids))
    #     lines_data = self.env['account.move'].search(domain)
    #     existing_branches = lines_data.mapped('branch_id')
    #     report_data = []
    #     branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in existing_branches]
    #     print('bvbvbvbvbvbvbvb',branches)
    #     for branch in existing_branches:
    #         current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
    #         print('dddd', branch.name)
    #         total_price_branch = sum([sum(move.line_ids.mapped('price_total')) for move in
    #                                   current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])
    #         total_out_refund_branch = sum([sum(move.line_ids.mapped('price_total')) for move in
    #                                        current_branch_lines.filtered(lambda x: x.move_type == 'out_refund')])
    #         total_out_refund_price_branch = sum([sum(move.line_ids.mapped('purchase_price')) for move in
    #                                              current_branch_lines.filtered(lambda x: x.move_type == 'out_refund')])
    #         total_out_refund_gty_branch = sum([sum(move.line_ids.mapped('quantity')) for move in
    #                                            current_branch_lines.filtered(lambda x: x.move_type == 'out_refund')])
    #         total = total_out_refund_gty_branch * total_out_refund_price_branch
    #         total_discount_branch = sum([sum(move.line_ids.mapped('discount')) for move in
    #                                      current_branch_lines.filtered(lambda x: x.move_type != 'out_refund')])
    #         total_net_cost_branch = total_price_branch - total_discount_branch
    #
    #         for account in current_branch_lines:
    #             invoice_number = account.name
    #             seller_name = account.created_by_id.name
    #             customer_name = account.partner_id.name
    #             invoice_date = account.invoice_date
    #             # cost = sum(account.line_ids.mapped('purchase_price'))
    #             payment_method = account.payment_method
    #             if account.move_type != 'out_refund':
    #                 total_price = sum(account.line_ids.mapped('price_total'))
    #                 cost = sum(account.line_ids.mapped('purchase_price')) * sum(account.line_ids.mapped('quantity'))
    #             else:
    #                 total_price = 0
    #                 cost = 0
    #
    #             total_discount = sum(account.line_ids.mapped('discount'))
    #             net_cost = total_price - total_discount
    #             if payment_method == 'option1':
    #                 payment_method = 'نقدى'
    #             elif payment_method == 'option2':
    #                 payment_method = 'اجل'
    #             else:
    #                 payment_method = '-'
    #
    #             if account.move_type == 'out_refund':
    #                 t = sum(account.line_ids.mapped('purchase_price')) * sum(account.line_ids.mapped('quantity'))
    #                 total_credit_note = sum(account.line_ids.mapped('price_total'))
    #             else:
    #                 t = 0
    #                 total_credit_note = 0
    #
    #             wizard_data = self.read()[0]
    #
    #             report_data_item = {
    #                 'branch_name': branch.name,
    #                 'invoice_number': invoice_number,
    #                 'seller_name': seller_name,
    #                 'customer_name': customer_name,
    #                 'invoice_date': invoice_date,
    #                 'cost': cost,
    #                 'payment_method': payment_method,
    #                 'total_price': total_price,
    #                 'total_discount': total_discount,
    #                 'net_cost': net_cost,
    #                 'total_credit_note': total_credit_note,
    #                 't': t,
    #             }
    #             report_data.append(report_data_item)
    #     data = {
    #         'form': wizard_data,
    #         'data': report_data,
    #         'branches':branches,
    #     }
    #     print('ddddddddddddddddddddddddddddddddddd',report_data)
    #     return self.env.ref("sb_sale_edit_and_reports.sales_report").report_action(self, data=data)
