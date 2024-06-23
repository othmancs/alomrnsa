"""init python files"""
from . import controllers
from . import models
from odoo.tools import column_exists, create_column


def pre_init_hook(cr):
    if not column_exists(cr, "res_users", "cannot_edit_unit_price"):
        create_column(cr, "res_users", "cannot_edit_unit_price", "bool")