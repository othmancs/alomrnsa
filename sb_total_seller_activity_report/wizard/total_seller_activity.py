from odoo import fields, models


class SellerActivityWizard(models.TransientModel):
    _name = 'seller.activity.wizard'

    branch_ids = fields.Many2many('res.branch', string="Branch", required=True)
    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="Printed By", compute="_compute_printed_by")
    print_date = fields.Date(string="Print Date", default=fields.Date.context_today)

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

        created_by_records = self.env['account.move'].search(domain).mapped('created_by_id')
        created_by_ids = created_by_records.ids
        created_by_names = {rec.id: rec.name for rec in created_by_records}

        result = {'option1': {}, 'option2': {}}

        for payment_method in ['option1', 'option2']:
            for created_by_id in created_by_ids:
                domain_credit_note = domain + [('move_type', '=', 'out_refund'), ('state', '=', 'posted'),
                                               ('created_by_id', '=', created_by_id),
                                               ('payment_method', '=', payment_method)]
                domain_invoice = domain + [('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
                                           ('created_by_id', '=', created_by_id),
                                           ('payment_method', '=', payment_method)]

                credit_notes = self.env['account.move'].search(domain_credit_note)
                invoices = self.env['account.move'].search(domain_invoice)

                credit_notes_sum = sum(credit_note.amount_untaxed for credit_note in credit_notes)
                invoices_sum = sum(invoice.amount_untaxed for invoice in invoices)

                total_quantity_credit_notes = sum(
                    line.quantity for credit_note in credit_notes for line in credit_note.invoice_line_ids)
                total_quantity_invoices = sum(
                    line.quantity for invoice in invoices for line in invoice.invoice_line_ids)

                credit_notes_read = credit_notes.read(
                    ['name', 'partner_id', 'invoice_date', 'amount_total', 'payment_method', 'amount_untaxed',
                     'total_purchase_price'])
                invoices_read = invoices.read(
                    ['name', 'partner_id', 'invoice_date', 'amount_total', 'payment_method', 'amount_untaxed',
                     'total_purchase_price'])

                result[payment_method][created_by_id] = {
                    'name': created_by_names.get(created_by_id, ''),
                    'credit_notes': credit_notes_read,
                    'invoices': invoices_read,
                    'credit_notes_sum': credit_notes_sum,
                    'invoices_sum': invoices_sum,
                    'credit_notes_quantity': total_quantity_credit_notes,
                    'invoices_quantity': total_quantity_invoices,
                    'credit_notes_total_purchase_price': sum(
                        rec['total_purchase_price'] for rec in credit_notes_read),
                    'invoices_total_purchase_price': sum(invoice['total_purchase_price'] for invoice in invoices_read),
                }

        # Prepare data for the report template
        branch_data = []
        for branch in self.branch_ids:
            created_by_data = {}
            for created_by_id in created_by_ids:
                branch_domain = domain + [('branch_id', '=', branch.id), ('created_by_id', '=', created_by_id)]
                if self.env['account.move'].search_count(branch_domain) > 0:
                    # Ensure 'option1' and 'option2' are properly populated in result
                    data_option1 = result['option1'].get(created_by_id, {})
                    data_option2 = result['option2'].get(created_by_id, {})
                    created_by_data[created_by_id] = {
                        'name': created_by_names.get(created_by_id, ''),
                        'option1': data_option1,
                        'option2': data_option2,
                    }

            branch_data.append({
                'branch_name': branch.name,
                'created_by_data': created_by_data,
            })

        wizard_data = {
            'company_id': self.company_id.name,
            'branch_data': branch_data,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'printed_by': self.printed_by,
            'print_date': self.print_date,
        }

        data = {
            'form': wizard_data,
        }

        return self.env.ref("sb_total_seller_activity_report.seller_activity_report").report_action(self, data=data)



    def xls_report_action(self):
        domain = [('company_id', '=', self.company_id.id)]

        if self.branch_ids:
            domain += [('branch_id', 'in', self.branch_ids.ids)]

        if self.date_from:
            domain += [('invoice_date', '>=', self.date_from)]

        if self.date_to:
            domain += [('invoice_date', '<=', self.date_to)]

        created_by_records = self.env['account.move'].search(domain).mapped('created_by_id')
        created_by_ids = created_by_records.ids
        created_by_names = {record.id: record.name for record in created_by_records}

        result = {'option1': {}, 'option2': {}}

        for payment_method in ['option1', 'option2']:
            for created_by_id in created_by_ids:
                domain_credit_note = domain + [('move_type', '=', 'out_refund'), ('state', '=', 'posted'),
                                               ('created_by_id', '=', created_by_id),
                                               ('payment_method', '=', payment_method)]
                domain_invoice = domain + [('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
                                           ('created_by_id', '=', created_by_id),
                                           ('payment_method', '=', payment_method)]

                credit_notes = self.env['account.move'].search(domain_credit_note)
                invoices = self.env['account.move'].search(domain_invoice)

                credit_notes_sum = sum(credit_note.amount_untaxed for credit_note in credit_notes)
                invoices_sum = sum(invoice.amount_untaxed for invoice in invoices)

                total_quantity_credit_notes = sum(
                    line.quantity for credit_note in credit_notes for line in credit_note.invoice_line_ids)
                total_quantity_invoices = sum(
                    line.quantity for invoice in invoices for line in invoice.invoice_line_ids)

                credit_notes_read = credit_notes.read(
                    ['name', 'partner_id', 'invoice_date', 'amount_total', 'payment_method', 'amount_untaxed',
                     'total_purchase_price'])
                invoices_read = invoices.read(
                    ['name', 'partner_id', 'invoice_date', 'amount_total', 'payment_method', 'amount_untaxed',
                     'total_purchase_price'])

                result[payment_method][created_by_id] = {
                    'name': created_by_names.get(created_by_id, ''),
                    'credit_notes': credit_notes_read,
                    'invoices': invoices_read,
                    'credit_notes_sum': credit_notes_sum,
                    'invoices_sum': invoices_sum,
                    'credit_notes_quantity': total_quantity_credit_notes,
                    'invoices_quantity': total_quantity_invoices,
                    'credit_notes_total_purchase_price': sum(
                        rec['total_purchase_price'] for rec in credit_notes_read),
                    'invoices_total_purchase_price': sum(invoice['total_purchase_price'] for invoice in invoices_read),
                }

        # Prepare data for the report template
        branch_data = []
        for branch in self.branch_ids:
            created_by_data = {}
            for created_by_id in created_by_ids:
                branch_domain = domain + [('branch_id', '=', branch.id), ('created_by_id', '=', created_by_id)]
                if self.env['account.move'].search_count(branch_domain) > 0:
                    # Ensure 'option1' and 'option2' are properly populated in result
                    data_option1 = result['option1'].get(created_by_id, {})
                    data_option2 = result['option2'].get(created_by_id, {})
                    created_by_data[created_by_id] = {
                        'name': created_by_names.get(created_by_id, ''),
                        'option1': data_option1,
                        'option2': data_option2,
                    }

            branch_data.append({
                'branch_name': branch.name,
                'created_by_data': created_by_data,
            })

        wizard_data = {
            'company_id': self.company_id.name,
            'branch_data': branch_data,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'printed_by': self.printed_by,
            'print_date': self.print_date,
        }

        data = {
            'form': wizard_data,
        }
        return self.env.ref("sb_total_seller_activity_report.seller_activity_report_xls").report_action(self, data=data)
