# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models


class MultiBranch(models.Model):
    _name = 'res.branch'
    _description = "Branch"

    # _inherit = 'res.branch'
    _inherits = {'hr.branch': 'hr_branch_id'}

    hr_branch_id = fields.Many2one('hr.branch', 'HR Branch', ondelete='cascade', auto_join=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('hr_branch_id'):
                branch = self.env['hr.branch'].create({
                    'name': vals['name'],
                    'code': vals['name'],
                    'company_id': vals.get('company_id'),
                })
                vals['hr_branch_id'] = branch.id
        res = super(MultiBranch, self).create(vals_list)
        for rec in res:
            if vals['hr_branch_id']:
                hr_branch = self.env['hr.branch'].browse(vals['hr_branch_id'])
                hr_branch.branch_id = rec.id
        return res


class HRBranch(models.Model):
    _inherit = 'hr.branch'

    branch_id = fields.Many2one("res.branch", string="Branch")
