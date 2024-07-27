from odoo import fields, models, api
from hijri_converter import Gregorian
from collections import defaultdict


class SalesPerDayWizard(models.TransientModel):
    _name = 'sales.per.day.wizard'

    branch_ids = fields.Many2many('res.branch', string="Branch", required=True)
    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="Printed By", compute="_compute_printed_by")
    print_date = fields.Date(string="Print Date", default=fields.Date.context_today)

    @api.depends('branch_ids', 'date_from', 'date_to', 'company_id')
    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def pdf_report_action(self):
        domain = [('company_id', '=', self.company_id.id)]

        if self.branch_ids:
            domain += [('branch_id', 'in', self.branch_ids.ids)]

        if self.date_from:
            domain += [('invoice_date', '>=', self.date_from)]

        if self.date_to:
            domain += [('invoice_date', '<=', self.date_to)]

        domain_credit_note = domain + [('move_type', '=', 'out_refund'), ('state', '=', 'posted')]
        domain_invoice = domain + [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]

        credit_notes = self.env['account.move'].search(domain_credit_note)
        invoices = self.env['account.move'].search(domain_invoice)

        # Aggregate data by branch and date
        branch_data = defaultdict(lambda: defaultdict(lambda: {
            'sales': 0.0,
            'returns': 0.0,
            'net_sales': 0.0,
            'cost': 0.0,
            'profit': 0.0,
            'quantity': 0
        }))

        for invoice in invoices:
            branch_id = invoice.branch_id.id
            date_str = invoice.invoice_date.strftime('%Y-%m-%d')
            branch_data[branch_id][date_str]['sales'] += invoice.amount_untaxed
            branch_data[branch_id][date_str]['quantity'] += sum(line.quantity for line in invoice.invoice_line_ids)
            branch_data[branch_id][date_str]['cost'] += invoice.total_purchase_price

        for credit_note in credit_notes:
            branch_id = credit_note.branch_id.id
            date_str = credit_note.invoice_date.strftime('%Y-%m-%d')
            branch_data[branch_id][date_str]['returns'] += credit_note.amount_untaxed

        # Calculate net sales and profit
        for branch_id, dates in branch_data.items():
            for date_str, data in dates.items():
                data['net_sales'] = data['sales'] - data['returns']
                data['profit'] = data['net_sales'] - data['cost']

        branch_data_final = []
        for branch_id in self.branch_ids.ids:
            branch = self.env['res.branch'].browse(branch_id)
            branch_records = []
            for date_str, data in sorted(branch_data[branch_id].items()):
                hijri_date = Gregorian(int(date_str[:4]), int(date_str[5:7]), int(date_str[8:])).to_hijri()
                day_name = fields.Date.from_string(date_str).strftime('%A')
                branch_records.append({
                    'day_name': day_name,
                    'hijri_date': hijri_date,
                    'invoice_date': date_str,
                    'sales': data['sales'],
                    'returns': data['returns'],
                    'net_sales': data['net_sales'],
                    'cost': data['cost'],
                    'profit': data['profit'],
                })
            branch_data_final.append({
                'branch_name': branch.name,
                'records': branch_records
            })

        wizard_data = self.read()[0]
        wizard_data['branch_names'] = ', '.join([branch.name for branch in self.branch_ids])
        wizard_data['branch_data'] = branch_data_final

        data = {
            'form': wizard_data,
            'credit_notes_sum': sum(data['returns'] for records in branch_data.values() for data in records.values()),
            'invoices_sum': sum(data['sales'] for records in branch_data.values() for data in records.values()),
            'credit_notes_quantity': sum(
                data['quantity'] for records in branch_data.values() for data in records.values()),
            'invoices_quantity': sum(data['quantity'] for records in branch_data.values() for data in records.values()),
            'total_purchase_price_sum': sum(
                data['cost'] for records in branch_data.values() for data in records.values()),
        }

        return self.env.ref("sb_sales_per_day_report.sales_per_day_report").report_action(self, data=data)

    def xls_report_action(self):
        domain = [('company_id', '=', self.company_id.id)]

        if self.branch_ids:
            domain += [('branch_id', 'in', self.branch_ids.ids)]

        if self.date_from:
            domain += [('invoice_date', '>=', self.date_from)]

        if self.date_to:
            domain += [('invoice_date', '<=', self.date_to)]

        domain_credit_note = domain + [('move_type', '=', 'out_refund'), ('state', '=', 'posted')]
        domain_invoice = domain + [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]

        credit_notes = self.env['account.move'].search(domain_credit_note)
        invoices = self.env['account.move'].search(domain_invoice)

        # Aggregate data by branch and date
        branch_data = defaultdict(lambda: defaultdict(lambda: {
            'sales': 0.0,
            'returns': 0.0,
            'net_sales': 0.0,
            'cost': 0.0,
            'profit': 0.0,
            'quantity': 0
        }))

        for rec in invoices:
            branch_id = rec.branch_id.id
            date_str = rec.invoice_date.strftime('%Y-%m-%d')
            branch_data[branch_id][date_str]['sales'] += rec.amount_untaxed
            branch_data[branch_id][date_str]['quantity'] += sum(line.quantity for line in rec.invoice_line_ids)
            branch_data[branch_id][date_str]['cost'] += rec.total_purchase_price

        for rec in credit_notes:
            branch_id = rec.branch_id.id
            date_str = rec.invoice_date.strftime('%Y-%m-%d')
            branch_data[branch_id][date_str]['returns'] += rec.amount_untaxed

        # Calculate net sales and profit
        for branch_id, dates in branch_data.items():
            for date_str, data in dates.items():
                data['net_sales'] = data['sales'] - data['returns']
                data['profit'] = data['net_sales'] - data['cost']

        branch_data_final = []
        for branch_id in self.branch_ids.ids:
            branch = self.env['res.branch'].browse(branch_id)
            branch_records = []
            for date_str, data in sorted(branch_data[branch_id].items()):
                hijri_date = Gregorian(int(date_str[:4]), int(date_str[5:7]), int(date_str[8:])).to_hijri()
                day_name = fields.Date.from_string(date_str).strftime('%A')
                branch_records.append({
                    'day_name': day_name,
                    'hijri_date': hijri_date,
                    'invoice_date': date_str,
                    'sales': data['sales'],
                    'returns': data['returns'],
                    'net_sales': data['net_sales'],
                    'cost': data['cost'],
                    'profit': data['profit'],
                })
            branch_data_final.append({
                'branch_name': branch.name,
                'records': branch_records
            })

        wizard_data = self.read()[0]
        wizard_data['branch_names'] = ', '.join([branch.name for branch in self.branch_ids])
        wizard_data['branch_data'] = branch_data_final

        data = {
            'form': wizard_data,
            'credit_notes_sum': sum(data['returns'] for records in branch_data.values() for data in records.values()),
            'invoices_sum': sum(data['sales'] for records in branch_data.values() for data in records.values()),
            'credit_notes_quantity': sum(
                data['quantity'] for records in branch_data.values() for data in records.values()),
            'invoices_quantity': sum(data['quantity'] for records in branch_data.values() for data in records.values()),
            'total_purchase_price_sum': sum(
                data['cost'] for records in branch_data.values() for data in records.values()),
        }
        return self.env.ref("sb_sales_per_day_report.sales_per_day_report_xls").report_action(self, data=data)
