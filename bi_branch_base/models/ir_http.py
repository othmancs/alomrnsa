# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import hashlib
import json
from odoo import api, models
from odoo.http import request
from odoo.tools import ustr
import odoo


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        """ Add information about iap enrich to perform """
        user = request.env.user
        session_info = super(Http, self).session_info()

        if self.env.user.has_group('base.group_user'):
            session_info.update({
                # current_company should be default_company
                "user_companies": {
                    'current_company': user.company_id.id,
                    'allowed_companies': {
                        comp.id: {
                            'id': comp.id,
                            'name': comp.name,
                        } for comp in user.company_ids
                    },
                },
                "user_branches": {
                    'current_branch': user.branch_id.id,
                    'allowed_branches': {
                        comp.id: {
                            'id': comp.id,
                            'name': comp.name,
                            'company': comp.company_id.id,
                        } for comp in user.branch_ids
                    },
                },
                "currencies": self.get_currencies(),
                "show_effect": True,
                "display_switch_company_menu": user.has_group('base.group_multi_company') and len(user.company_ids) > 1,
                "display_switch_branch_menu": user.has_group('bi_branch_base.group_multi_branch') and len(
                    user.branch_ids) > 1,
                "allowed_branch_ids": user.branch_id.ids
            })
        return session_info

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
