from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountReportWizard(models.TransientModel):
    _name = 'account.report.wizard'

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(required=True, default=lambda self: fields.Date.context_today(self), string="End Date")
    state = fields.Selection(selection=[
        ('all', 'All'),
        ('posted', 'Posted'),
        ('draft', 'Unposted'),
    ], string='Status', required=True, default='all')

    account_id = fields.Many2one('account.account', string="Account", required=True)
    
    def check_date_range(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('End Date should be greater than Start Date.'))

    def print_pdf(self):
        date_from = self.date_from
        date_to = self.date_to
        state = self.state
        account_id = self.account_id.id
        account_name = self.account_id.name
        self.check_date_range()
        datas = {
            'start_date': date_from,
            'end_date': date_to,
            'state': state,
            'account_id': account_id,
            'account_name': account_name,
        }
        return self.env.ref('kb_account_reports.action_account_report_template').report_action(self, data=datas)


    def print_xlsx(self):
        print("xlsx")
        self.check_date_range()

        date_from = self.date_from
        date_to = self.date_to
        state = self.state
        account_id = self.account_id.id
        account_name = self.account_id.name
        datas = {
            'id': self.id,
            'start_date': date_from,
            'end_date': date_to,
            'state': state,
            'account_id': account_id,
            'account_name': account_name,
        }
        return self.env.ref('kb_account_reports.action_account_report_xlsx').report_action(self, data=datas)
