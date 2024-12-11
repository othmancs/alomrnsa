# -*- coding: utf-8 -*-


from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.http import content_disposition, Controller, request, route


class CustomerPortal(CustomerPortal):

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        menus = request.env['portal.portal'].sudo().search([], order='sequence')
        values.update({'menus': menus})
        return request.render("portal.portal_my_home", values)


