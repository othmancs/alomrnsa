#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class WorkLocation(models.Model):
    _inherit = "hr.work.location"

    project_id = fields.Many2one('project.project', 'المشروع', index=True, copy=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string="الحساب التحليلي", copy=False)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.analytic_account_id = False
        if self.project_id.id:
            analytic_account_id = self.env['account.analytic.account'].search([('project_ids', 'in', [self.project_id.id])], limit=1)
            self.analytic_account_id = analytic_account_id

