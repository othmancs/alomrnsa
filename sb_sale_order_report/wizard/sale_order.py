from odoo import fields, models


class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'

    branch_ids = fields.Many2many('res.branch', string="الفــرع", required=True)
    date_from = fields.Date(string="مـن تـاريـخ", required=True)
    date_to = fields.Date(string="إلـى تـاريـخ", required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def pdf_report_action(self):
        domain = []
        branch_ids = self.branch_ids
        if branch_ids:
            domain += [('branch_id', 'in', branch_ids.ids)]
        date_from = self.date_from
        if date_from:
            domain += [('date_order', '>=', date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('date_order', '<=', date_to)]

        domain += [('company_id', '=', self.company_id.id)]

        wizard_data = self.read()[0]

        branches = self.env['res.branch'].browse(wizard_data['branch_ids'])
        branch_dicts = [{'branch_name': name.name} for name in branches]
        print("all_branches=====", branch_dicts)

        wizard_data['branch_names'] = branch_dicts

        sale_orders = self.env['sale.order'].search_read(domain)
        branch_sale_orders = {}
        for order in sale_orders:
            branch_name = self.env['res.branch'].browse(order['branch_id'][0]).name
            if branch_name not in branch_sale_orders:
                branch_sale_orders[branch_name] = []
            branch_sale_orders[branch_name].append(order)

        # Separate the first branch and the rest
        branch_list = list(branch_sale_orders.items())
        first_branch = branch_list[0] if branch_list else (None, [])
        other_branches = branch_list[1:]

        # Prepare the data dictionary for the report
        data = {
            'form': wizard_data,
            'first_branch': first_branch,
            'other_branches': other_branches,
        }
        return self.env.ref("sb_sale_order_report.sale_order_report").report_action(self, data=data)

    def xls_report_action(self):
        domain = []
        branch_ids = self.branch_ids
        if branch_ids:
            domain += [('branch_id', 'in', branch_ids.ids)]
        date_from = self.date_from
        if date_from:
            domain += [('date_order', '>=', date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('date_order', '<=', date_to)]

        domain += [('company_id', '=', self.company_id.id)]

        wizard_data = self.read()[0]

        branches = self.env['res.branch'].browse(wizard_data['branch_ids'])
        branch_names = ', '.join([branch['name'] for branch in branches])

        wizard_data['branch_names'] = branch_names

        sale_order = self.env['sale.order'].search_read(domain)

        data = {
            'form': wizard_data,
            'sale_order': sale_order,
        }
        return self.env.ref("sb_sale_order_report.sale_order_report_xls").report_action(self, data=data)
