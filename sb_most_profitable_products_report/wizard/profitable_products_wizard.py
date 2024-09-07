from odoo import models, fields


class BranchSalesComparison(models.TransientModel):
    _name = 'profitable.products.wizard'
    _description = 'profitable_products_wizard'

    date_start = fields.Date(string="تاريخ البدايه", required=True)
    date_end = fields.Date(string="تاريخ النهايه", required=True)
    branch_id = fields.Many2many('res.branch', string="الفرع", required=True)
    product_ids = fields.Many2many('product.product', string="المنتج")
    check_all_products= fields.Boolean(string="كل المنتجات")
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def generate_pdf_report(self):
        domain = [
            ('invoice_date', '>=', self.date_start),
            ('invoice_date', '<=', self.date_end),
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice'),
            ('branch_id', 'in', self.branch_id.ids)  # Use 'in' if branch_id can be multiple
        ]

        if self.check_all_products == False:
            domain.append(
                ('invoice_line_ids.product_id', 'in', self.product_ids.ids)
            )

        lines_data = self.env['account.move'].search(domain)
        existing_branch = lines_data.mapped('branch_id')
        existing_products = list(set(lines_data.mapped('invoice_line_ids.product_id')))
        if self.check_all_products == False:
            existing_product_2 = [product for product in existing_products if product in self.product_ids]
        else:
            existing_product_2 = existing_products

        report_data = []

        branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in existing_branch]
        print('ssssssssssssss', branches)
        for branch in existing_branch:
            current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)
            for product in existing_product_2:

                product_ref = product.default_code
                product_name = product.name
                product_qty = sum(
                    current_branch_lines.invoice_line_ids.filtered(lambda x: x.product_id == product).mapped('quantity'))
                product_price = sum(current_branch_lines.invoice_line_ids.mapped(lambda x: x.price_unit * x.quantity and x.product_id == product ))
                product_cost = sum(
                    current_branch_lines.invoice_line_ids.mapped(lambda x: x.purchase_price * x.quantity and x.product_id == product))
                profit= round(product_price-product_cost,2)
                profit2= round((profit /product_qty)*100 ,2)
                domain_on_hand = [
                    # ('date','<',obj.date_start),
                    ('location_id.branch_id', '=', branch.id),
                    # ('branch_id','=',branch.id)
                ]
                on_hand = self.env['stock.quant'].search(domain_on_hand)
                product_qty_in = round(sum(
                    on_hand.filtered(lambda x: x.product_id == product).mapped(
                        'quantity')
                ), 2)


                report_data_item = {
                    'branch_name': branch.name,
                    "product_ref": product_ref,
                    "product_name": product_name,
                    "product_qty": product_qty,
                    "product_on_hand_qty": product_qty_in,
                    "profit": profit,
                    "profit_2": profit2,
                }

                report_data.append(report_data_item)
        print('reeeeeeeeeeeee', report_data)
        data = {
            'form': self.read()[0],
            'data': report_data,
            'branches': branches,
        }
        return self.env.ref("sb_most_profitable_products_report.profitable_products_report").report_action(self, data=data)