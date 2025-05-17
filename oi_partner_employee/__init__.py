from . import models
from odoo.api import Environment, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env['res.partner'].search([])._calc_employee()