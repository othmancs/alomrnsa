# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
import base64
from odoo.tools import groupby
from datetime import datetime


class EquipmentInspection(http.Controller):

    @http.route('/redirect_equipment_inspenction/<model("maintenance.equipment"):equipment>', auth='user', type='http', website=True, csrf=False)
    def get_equipment_inspection(self, equipment, **kw):
        run_inspection = request.env.ref('saudi_hr_it_operations.action_equipment_run_inspection')
        open_inspection = equipment.open_run_inspection()
        inspection_id = request.env['equipment.run.inspection'].with_context(open_inspection.get('context')).create({})
        return request.redirect('/web#model=equipment.run.inspection&id=%s&action=%s&view_type=form' % (inspection_id.id, run_inspection.id))
