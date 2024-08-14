from odoo import models, fields


class BranchSalesComparison(models.TransientModel):
    _name = 'quantities.sold.wizard'
    _description = 'quantities_sold_wizard'

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
        if len(self.product_category_id) == 1 and self.product_category_id.name == 'All':
            domain.append(('line_ids.product_id.categ_id.parent_id.name', '=', 'All'))
        else:
            domain.append(('line_ids.product_id.categ_id.id', 'in', self.product_category_id.ids))
        lines_data = self.env['account.move'].search(domain)
        existing_branch = lines_data.mapped('branch_id')
        existing_products = list(set(lines_data.mapped('line_ids.product_id')))
        print('existing_branch', existing_branch)
        report_data = []

        branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in existing_branch]
        print('ssssssssssssss', branches)
        for branch in existing_branch:
            current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
            for product in existing_products:
                product_ref = product.default_code
                product_name = product.name
                product_uom_name = ' حبه'
                product_qty = sum(
                    current_branch_lines.line_ids.filtered(lambda x: x.product_id == product).mapped('quantity'))
                domain_qty_all = [
                    ('state', '=', 'posted'),
                    ('move_type', '=', 'out_invoice'),
                    ('line_ids.product_id', '=', product.id)
                ]
                qty_all = self.env['account.move'].search(domain_qty_all)
                product_qty_all = sum(
                    qty_all.line_ids.filtered(lambda x: x.product_id == product).mapped('quantity'))
                domain_on_hand = [
                    # ('date','<',obj.date_start),
                    ('location_id.branch_id', '=', branch.id),
                    # ('branch_id','=',branch.id)
                ]
                on_hand = self.env['stock.quant'].search(domain_on_hand)
                product_qty_in = round(sum(
                    on_hand.filtered(lambda x: x.product_id == product).mapped(
                        'quantity')
                ), 4)

                report_data_item = {
                    'branch_name': branch.name,
                    "product_ref": product_ref,
                    "product_name": product_name,
                    "product_uom_name": product_uom_name,
                    "product_qty": product_qty,
                    "product_qty_all": product_qty_all,
                    "product_on_hand_qty": product_qty_in,
                }

                report_data.append(report_data_item)
        print('reeeeeeeeeeeee', report_data)
        data = {
            'form': self.read()[0],
            'data': report_data,
            'branches': branches,
        }
        return self.env.ref("sb_quantities_sold_report.quantities_sold_report").report_action(self, data=data)