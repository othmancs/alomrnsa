from odoo import models, fields


class BranchSalesComparison(models.TransientModel):
    _name = 'profitable.clients.wizard'
    _description = 'profitable_clients_wizard'

    date_start = fields.Date(string="تاريخ البدايه", required=True)
    date_end = fields.Date(string="تاريخ النهايه", required=True)
    branch_id = fields.Many2one('res.branch', string="الفرع", required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def get_clients_export_xlsx(self):
        return self.env.ref("sb_profitable_clients_report.report_profitable_clients").report_action(self)

    def generate_pdf_report(self):
        report_data = []
        domain = [('invoice_date', '>=', self.date_start),
                  ('invoice_date', '<=', self.date_end),
                  ('state', '=', 'posted'),
                  ('move_type', '=', 'out_invoice'),
                  ('branch_id', '=', self.branch_id.id)
                  ]
        lines_data = self.env['account.move'].search(domain)
        existing_client = lines_data.mapped('invoice_partner_display_name')
        existing_clients = set()

        for client in existing_client:
            current_client_lines = lines_data.filtered(lambda x: x.invoice_partner_display_name == client)
            if client not in existing_clients:
                existing_clients.add(client)
                partner = self.env['res.partner'].search([('name', '=', client)], limit=1)
                other_id = partner.other_id
                unit_price_branch = sum([sum(move.mapped('amount_untaxed')) for move in
                                         current_client_lines.filtered(lambda x: x.move_type != 'out_refund')])

                total_cost_branch = sum(
                    [sum(move.line_ids.mapped(lambda line: line.purchase_price * line.quantity)) for move in
                     current_client_lines.filtered(lambda x: x.move_type != 'out_refund')])

                print('client', client)
                cost = abs(unit_price_branch - total_cost_branch)

                if total_cost_branch > 0:
                    cost_pers = (cost / total_cost_branch) * 100


            report_data_item = {
                "other_id": other_id,
                "client": client,
                "unit_price_branch": unit_price_branch,
                "total_cost_branch": total_cost_branch,
                "cost": cost,
                "cost_pers": cost_pers,

            }
            report_data.append(report_data_item)
        data = {
            'form': self.read()[0],
            'data': report_data
        }
        return self.env.ref("sb_profitable_clients_report.profitable_clients_report").report_action(self, data=data)
