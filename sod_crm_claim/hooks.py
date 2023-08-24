# Copyright 2019-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    warehouse = env.ref("stock.warehouse0")
    rma_type_id = env.ref("sod_crm_claim.picking_type_rma").id
    warehouse.write(
        {
            "rma_type_id": rma_type_id,
        }
    )
