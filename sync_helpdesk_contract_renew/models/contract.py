# -*- coding: utf-8 -*-
# Part of Synconics. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class Contract(models.Model):
    _inherit = 'contract.contract'
    _description = 'Contract'

    def renew_contract(self):
        """
            Renew contract depends on dates
        """
        date_start = False
        if self.date_end < fields.Datetime.now():
            date_start = fields.Datetime.now()
        else:
            date_start = self.date_end + relativedelta(days=1)
        contract_period_status = False
        if self.contract_period == 'years':
            contract_period_status = date_start + relativedelta(years=1, days=-1)
        elif self.contract_period == 'months':
            contract_period_status = date_start + relativedelta(months=1, days=-1)
        elif self.contract_period == 'weeks':
            contract_period_status = date_start + relativedelta(weeks=1, days=-1)
        elif self.contract_period == 'days':
            contract_period_status = date_start
        renew_contract_id = self.copy()
        renew_contract_id.update({'date_end':  contract_period_status,
                                  'date_start': date_start})
        form_id = self.env.ref('sync_helpdesk_contract.contract_contract_form_view')
        return {
            'name': _('Renew Contract'),
            'view_mode': 'form',
            'view_id': [form_id.id],
            'res_model': 'contract.contract',
            'context': dict(self.env.context),
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': renew_contract_id.id,
        }
