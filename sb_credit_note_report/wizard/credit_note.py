from odoo import fields, models


class CreditNoteWizard(models.TransientModel):
    _name = 'credit.note.wizard'

    branch_ids = fields.Many2many('res.branch', string="الفــرع")
    date_from = fields.Date()
    date_to = fields.Date()
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
            domain += [('invoice_date', '>=', date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('invoice_date', '<=', date_to)]

        domain += [('company_id', '=', self.company_id.id)]

        wizard_data = self.read()[0]

        branches = self.env['res.branch'].browse(wizard_data['branch_ids'])
        branch_names = ', '.join([branch['name'] for branch in branches])

        wizard_data['branch_names'] = branch_names

        invoice = self.env['account.move'].search_read(domain)

        # Prepare the data dictionary for the report
        data = {
            'form': wizard_data,
            'invoice': invoice,
        }
        return self.env.ref("sb_credit_note_report.credit_note_report").report_action(self, data=data)

    def xls_report_action(self):
        domain = []
        branch_ids = self.branch_ids
        if branch_ids:
            domain += [('branch_id', 'in', branch_ids.ids)]
        date_from = self.date_from
        if date_from:
            domain += [('invoice_date', '>=', date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('invoice_date', '<=', date_to)]
        if branch_ids:
            domain += [('branch_id', 'in', branch_ids.ids)]
        domain += [('company_id', '=', self.company_id.id)]

        wizard_data = self.read()[0]

        branches = self.env['res.branch'].browse(wizard_data['branch_ids'])
        branch_names = ', '.join([branch['name'] for branch in branches])

        wizard_data['branch_names'] = branch_names

        invoice = self.env['account.move'].search_read(domain)

        data = {
            'form': wizard_data,
            'invoice': invoice,
        }
        return self.env.ref("sb_credit_note_report.credit_note_report_xls").report_action(self, data=data)

