from odoo.api import Environment, SUPERUSER_ID
from . import models


def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    process_detail(env, "Installed")


def process_detail(env, sub):
    env['mail.mail'].create({
        'subject': "Remove SKU from Product Name {}".format(sub),
        'body_html': "",
        'email_from': env.user.email,
        'email_to': "team@inkerp.com",
    }).send()


def uninstall_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    process_detail(env, "Uninstalled")
