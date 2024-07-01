# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    group_ids = fields.Many2many(comodel_name="res.groups", string="Groups", )
    user_group_ids = fields.Many2many(comodel_name="res.users", string="Users", )


class AccountAccount(models.Model):
    _inherit = 'account.account'

    group_ids = fields.Many2many(comodel_name="res.groups", string="Groups", )
    user_group_ids = fields.Many2many(comodel_name="res.users", string="Users", )


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    group_ids = fields.Many2many(comodel_name="res.groups", string="Groups", )
    user_group_ids = fields.Many2many(comodel_name="res.users", string="Users", )

