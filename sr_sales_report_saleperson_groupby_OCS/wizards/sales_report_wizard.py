from odoo import models, fields, api, _

class SalesReportBySalesperson(models.TransientModel):
    _name = 'sale.salesperson.report'
    _description = 'Sales Report by Creator (created_by_id)'

    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)
    salesperson_ids = fields.Many2many(
        'res.users', 
        string="Salesperson (Creator)", 
        required=True,
        # اختيار المستخدمين الذين لديهم أوامر مبيعات كمُنشئين (created_by_id)
        domain=lambda self: [('id', 'in', self._get_available_creators().ids)]
    )

    def _get_available_creators(self):
        """ترجع قائمة بالمستخدمين الذين قاموا بإنشاء أوامر مبيعات"""
        sale_orders = self.env['sale.order'].search([])
        creator_ids = sale_orders.mapped('created_by_id').ids
        return self.env['res.users'].browse(creator_ids)

    def print_sale_report_by_salesperson(self):
        sales_orders = self.env['sale.order'].search([
            ('date_order', '>=', self.start_date),
            ('date_order', '<=', self.end_date),
            ('created_by_id', 'in', self.salesperson_ids.ids)
        ])

        sale_order_groupby_dict = {}
        for salesperson in self.salesperson_ids:
            # تصفية الأوامر حسب created_by_id
            filtered_orders = sales_orders.filtered(lambda o: o.created_by_id == salesperson)
            sale_order_groupby_dict[salesperson.name] = filtered_orders

        final_dist = {}
        for salesperson, orders in sale_order_groupby_dict.items():
            sale_data = []
            for order in orders:
                sale_data.append([
                    order.name,
                    order.date_order,
                    order.partner_id.name,
                    order.amount_total,
                ])
            final_dist[salesperson] = sale_data

        datas = {
            'ids': self.ids,
            'model': 'sale.salesperson.report',
            'form': final_dist,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

        return self.env.ref('sr_sales_report_saleperson_groupby.action_report_by_salesperson').report_action(self, data=datas)
