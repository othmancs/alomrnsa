from odoo import models, fields, api, _

class SalesReportBySalesperson(models.TransientModel):
    _name = 'sale.salesperson.report'
    _description = 'Sales Report by Salesperson'

    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)
    salesperson_ids = fields.Many2many('res.users', string="Salesperson", required=True)

    def print_sale_report_by_salesperson(self):
        sales_order = self.env['sale.order'].search([])
        sale_order_groupby_dict = {}
        for salesperson in self.salesperson_ids:
            # تغيير من x.user_id إلى x.created_by_id
            filtered_sale_order = list(filter(lambda x: x.created_by_id == salesperson, sales_order))
            filtered_by_date = list(
                filter(lambda x: self.start_date <= x.date_order <= self.end_date, filtered_sale_order))
            sale_order_groupby_dict[salesperson.name] = filtered_by_date

        final_dist = {}
        for salesperson in sale_order_groupby_dict.keys():
            sale_data = []
            for order in sale_order_groupby_dict[salesperson]:
                temp_data = [
                    order.name,
                    order.date_order,
                    order.partner_id.name,
                    order.amount_total,
                ]
                sale_data.append(temp_data)
            final_dist[salesperson] = sale_data

        datas = {
            'ids': self.ids,
            'model': 'sale.salesperson.report',
            'form': final_dist,
            'start_date': self.start_date,
            'end_date': self.end_date
        }

        return self.env.ref('sr_sales_report_saleperson_groupby.action_report_by_salesperson').report_action(self,data=datas)