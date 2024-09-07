from odoo import fields, models, api


class ProfitLossByCategory(models.TransientModel):
    _name = 'profit.loss.by.category.wizard'

    branch_ids = fields.Many2many('res.branch', string="الفــروع", required=True)
    product_category_ids = fields.Many2many('product.category', string="الفـئة")
    all_category = fields.Boolean(string="كل الفئات", default=False)
    date_from = fields.Date(string="مـن تــاريـخ", required=True)
    date_to = fields.Date(string="إلـي تــاريخ", required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبــع بـواسـطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تــاريـخ الطـباعــة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    @api.onchange('all_category', 'branch_ids')
    def _onchange_all_category(self):
        if self.all_category:
            related_categories = self.env['product.category'].search([])
            self.product_category_ids = related_categories
        else:
            self.product_category_ids = False

    def pdf_report_action(self):
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('branch_id', 'in', self.branch_ids.ids),
            ('invoice_line_ids.product_id.categ_id', 'in', self.product_category_ids.ids)
        ]

        lines_data = self.env['account.move'].search(domain)
        existing_branches = lines_data.mapped('branch_id').sorted(key=lambda b: self.branch_ids.ids.index(b.id))
        existing_categories = lines_data.mapped('invoice_line_ids.product_id.categ_id').filtered(
            lambda c: c.id in self.product_category_ids.ids)

        report_data = {}
        for branch in existing_branches:
            current_branch_lines = lines_data.filtered(lambda x: x.branch_id == branch)


            domain_on_hand = [
                ('location_id.branch_id', '=', branch.id),
            ]
            on_hand = self.env['stock.quant'].search(domain_on_hand)

            for category in existing_categories:
                current_category_lines = current_branch_lines.invoice_line_ids.filtered(
                    lambda x: x.product_id.categ_id == category)

                if current_category_lines:
                    total_purchase_cost = sum(
                        [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                         current_category_lines.filtered(
                             lambda x: x.move_id.move_type == 'out_invoice')])



                    # total_option1_branch_purchase = sum(
                    #     [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                    #      current_category_lines.filtered(lambda x: x.move_id.payment_method == 'option1' and x.move_id.move_type == 'out_invoice')])
                    # total_option2_branch_purchase = sum(
                    #     [sum(move.mapped(lambda x: x.purchase_price * x.quantity)) for move in
                    #      current_category_lines.filtered(lambda x: x.move_id.payment_method == 'option2' and x.move_id.move_type == 'out_invoice')])

                    total_sales = sum(
                        [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                         current_category_lines.filtered(
                             lambda x: x.move_id.move_type == 'out_invoice')])




                    # total_option1_branch_price = sum(
                    #     [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                    #      current_category_lines.filtered(lambda x: x.move_id.payment_method == 'option1' and x.move_id.move_type == 'out_invoice')])
                    # total_option2_branch_price = sum(
                    #     [sum(move.mapped(lambda x: x.price_unit * x.quantity)) for move in
                    #      current_category_lines.filtered(lambda x: x.move_id.payment_method == 'option2' and x.move_id.move_type == 'out_invoice')])



                    # Calculate the total quantity in hand for the current branch and category

                    product_qty_in = round(sum(
                        on_hand.filtered(lambda x: x.product_id.categ_id == category).mapped('quantity')
                    ), 4)

                    # total_sales = total_option1_branch_price + total_option2_branch_price
                    # total_purchase_cost = total_option1_branch_purchase + total_option2_branch_purchase
                    total_profit = total_sales - total_purchase_cost
                    profit_rate = (total_profit / total_sales) * 100 if total_sales else 0

                    key = (branch.name, category.name)
                    if key not in report_data:
                        report_data[key] = {
                            'branch_name': branch.name,
                            'category': category.name,
                            'total_sales': 0,
                            'total_purchase_cost': 0,
                            'total_profit': 0,
                            'profit_rate': 0,
                            'product_qty_in': 0,
                        }
                    report_data[key]['total_sales'] += round(abs(total_sales), 2)
                    report_data[key]['total_purchase_cost'] += total_purchase_cost
                    report_data[key]['total_profit'] += total_profit
                    report_data[key]['profit_rate'] += profit_rate
                    report_data[key]['product_qty_in'] += product_qty_in

        # Convert report_data dictionary to a list
        report_data_list = list(report_data.values())
        branches = [{'branch_id': branch.id, 'branch_name': branch.name} for branch in existing_branches]
        data = {
            'form': self.read()[0],
            'branch_data': report_data_list,
            'branches': branches
        }
        return self.env.ref("sb_profit_loss_by_category_report.profit_loss_by_category_report_action").report_action(self, data=data)
