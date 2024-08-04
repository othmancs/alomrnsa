from odoo import models, fields


class BranchSalesComparison(models.TransientModel):
    _name = 'customer.movement.wizard'
    _description = 'customer_movement_wizard'

    date_start = fields.Date(string="تاريخ البدايه", required=True)
    date_end = fields.Date(string="تاريخ النهايه", required=True)
    branch_id = fields.Many2many('res.branch', string="الفرع", required=True)
    partner_id = fields.Many2many('res.partner', string="العملاء",domain="[('branch_id', 'in', branch_id)]")
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def get_clients_export_xlsx(self):
        return self.env.ref("sb_customer_movement_report.report_customer_movement").report_action(self)

    def generate_pdf_report(self):
        report_data = []
        domain = [
            ('invoice_date', '>=', self.date_start),
            ('invoice_date', '<=', self.date_end),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('partner_id', 'in', self.partner_id.ids)
        ]
        lines_data = self.env['account.move'].search(domain)
        domain_new = [
            ('date', '<', self.date_start)
        ]

        balance_data = self.env['account.move.line'].search(domain_new)
        payment_domain = [
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('state', '=', 'posted')
        ]
        payment_data = self.env['account.payment'].search(payment_domain)
        processed_partner_ids = set()
        report_data = []
        branche = set()
        for line in lines_data:
            if line.partner_id.branch_id:
                branche.add(line.partner_id.branch_id)
        branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in branche]
        print('ddddd',branches)
        for branch in self.branch_id:
            branch_lines_data = lines_data.filtered(lambda x: x.partner_id.branch_id == branch)
            if branch_lines_data:
                for account in branch_lines_data:
                    if account.partner_id.id not in processed_partner_ids:
                        other_id = account.partner_id.other_id
                        partner_name = account.partner_id.name
                        processed_partner_ids.add(account.partner_id.id)
                        filtered_accounts = balance_data.filtered(lambda
                                                                      x: x.partner_id == account.partner_id and x.account_id == account.partner_id.property_account_receivable_id)
                        debit = round(sum(filtered_accounts.mapped('debit')), 4)
                        credit = round(sum(filtered_accounts.mapped('credit')), 4)
                        balance = debit - credit
                        unit_price_branch = sum([sum(move.mapped('amount_total_signed')) for move in
                                                 branch_lines_data.filtered(
                                                     lambda x: x.move_type == 'out_invoice')])

                        out_refund = self.env['account.move'].search([
                            ('move_type', '=', 'out_refund'),
                            ('partner_id', '=', account.partner_id.id),
                            ('state', '=', 'posted')
                        ])
                        out_refund_price = round(abs(sum(out_refund.mapped('amount_total_signed'))), 4)
                        in_refund = self.env['account.move'].search([
                            ('debit_origin_id', '=', account.debit_origin_id.id),
                            ('partner_id', '=', account.partner_id.id),
                            ('state', '=', 'posted')
                        ])
                        in_refund_price = round(abs(sum(in_refund.mapped('amount_total_signed'))), 4)
                        total_price_branch = round(abs(unit_price_branch - in_refund_price), 4)
                        filtered_payments = payment_data.filtered(lambda x: x.partner_id == account.partner_id)
                        payment = round(sum(filtered_payments.mapped('amount_company_currency_signed')), 4)
                        last_term_balance = round(abs(balance + unit_price_branch - payment), 4)
                        change_in_balance = round(abs(balance - last_term_balance), 4)
                        print('change_in_balance',change_in_balance)

            report_data_item = {
                'branch_name': branch.name,
                "other_id":other_id,
                "partner_name": partner_name,
                "balance": balance,
                "total_price_branch": total_price_branch,
                "in_refund_price": in_refund_price,
                "payment": payment,
                "out_refund_price": out_refund_price,
                "last_term_balance": last_term_balance,
                "change_in_balance": change_in_balance,

            }
            print('report_data_item',report_data_item)
            print('bbb',branches)
            report_data.append(report_data_item)
        data = {
            'form': self.read()[0],
            'data': report_data,
            'branches': branches,
        }
        return self.env.ref("sb_customer_movement_report.customer_movement_report").report_action(self, data=data)
