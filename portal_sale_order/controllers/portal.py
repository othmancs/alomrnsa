""" import section  """
import base64
from odoo.http import request
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
import json
from pytz import timezone, utc
import datetime


class SaleOrder(CustomerPortal):
    """
        Extending CustomerPortal to add 'Sale Order' menu
    """

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'sale_order_count' in counters:
            sale_order_count = request.env['sale.order'].search_count([
                ('user_id', '=', http.request.env.user.id)
            ])
            values['sale_order_count'] = sale_order_count
        return values

    @http.route('/my/sale_orders', type='http', website=True, auth='user')
    def sale_order_list_view(self):
        sale_orders = request.env['sale.order'].search([
            ('user_id', '=', request.env.user.id)
        ])

        vals = {
            'sale_orders': sale_orders,
            'page_name': 'sale_orders_list',
        }

        return request.render(
            'portal_sale_order.portal_my_sale_orders_list', vals
        )

    @http.route(['/my/sale_order/<int:sale_order_id>',
                 '/my/sale_order'
                 ], type='http', website=True, auth='user', methods=["POST", "GET"])
    def sale_order_form(self, sale_order_id=False, **post):

        partner_id = request.env['res.partner'].search([
            ('type', '!=', 'private'),
            ('company_id', 'in', (False, http.request.env.user.company_id.id))
        ])
        pricelist_id = request.env['product.pricelist'].search([
            ('company_id', 'in', (False, http.request.env.user.company_id.id))
        ])
        warehouse_id = request.env['stock.warehouse'].search([])
        branch_ids = http.request.env.user.branch_ids
        default_branch_id = http.request.env.user.branch_id
        products = http.request.env['product.product'].search([])

        vals = {
            'page_name': 'sale_order_form',
            'partner_id': partner_id,
            'pricelist_id': pricelist_id,
            'default_branch_id': default_branch_id,
            'branch_ids': branch_ids,
            'products': products,
            'warehouse_id': warehouse_id,
            'sale_order_id': False,
        }

        if request.httprequest.method == "POST":
            partner_id = int(post.get('partner_id') if post.get('partner_id') else False)
            pricelist_id = int(post.get('pricelist_id') if post.get('pricelist_id') else False)
            branch_id = int(post.get('branch_id') if post.get('branch_id') else False)
            is_sale_order = int(post.get('is_sale_order') if post.get('is_sale_order') else False)
            is_confirm = post.get('is_confirm') if post.get('is_confirm') else False

            line_items_json = post.get('line_items')
            line_items = json.loads(line_items_json) if line_items_json else []

            line_values = []
            for line_item in line_items:
                if line_item.get('product_id'):
                    product_id = request.env['product.product'].browse(int(line_item.get('product_id')))
                    line_values.append((0, 0, {
                        'name': product_id.name,
                        'product_id': product_id.id,
                        'product_template_id': product_id.product_tmpl_id.id,
                        'product_warehouse_id': int(
                            line_item.get('warehouse_id') if line_item.get('warehouse_id') else False),
                        'product_uom_qty': float(line_item.get('quantity', False)),
                        'price_unit': float(line_item.get('price_unit', False)),
                        'product_uom': product_id.uom_id.id,
                    }))
            if not is_sale_order:
                sale_order = request.env['sale.order'].sudo().create({
                    'pricelist_id': pricelist_id,
                    'partner_id': partner_id,
                    'branch_id': branch_id,
                    'order_line': line_values,
                    'user_id': request.env.user.id
                })
                if is_confirm:

                    sale_order.action_confirm()

                    vals.update({
                        'sale_order_id': sale_order
                    })
                    success_msg = 'The Sale Orders Was Successfully Confirmed'
                    vals['success_msg'] = success_msg
                else:
                    vals.update({
                        'sale_order_id': sale_order
                    })
                    success_msg = 'The Sale Orders Was Successfully Created'
                    vals['success_msg'] = success_msg
            else:
                existing_sale_order = request.env['sale.order'].browse(is_sale_order)
                lines = [(5, 0, 0)]
                existing_sale_order.sudo().write({
                    'order_line': lines
                })
                sale_order = existing_sale_order.sudo().write({
                    'pricelist_id': pricelist_id,
                    'partner_id': partner_id,
                    'branch_id': branch_id,
                    'order_line': line_values,
                    'user_id': request.env.user.id
                })
                if is_confirm:
                    existing_sale_order.sudo().action_confirm()

                    vals.update({
                        'sale_order_id': existing_sale_order
                    })
                    success_msg = 'The Sale Orders Was Successfully Confirmed'
                    vals['success_msg'] = success_msg
                else:
                    vals.update({
                        'sale_order_id': existing_sale_order
                    })
                    success_msg = 'The Sale Orders Was Successfully Updated'
                    vals['success_msg'] = success_msg
        else:
            if sale_order_id:
                sale_order = request.env['sale.order'].browse(sale_order_id)
                vals.update({
                    'sale_order_id': sale_order
                })
        return request.render(
            'portal_sale_order.portal_sale_order_form', vals
        )

    # @http.route(['/my/sale_order/create'], type='http', website=True)
    # def create_approval_request(self, **post):
    #
    #     """
    #         partner_id
    #         pricelist_id
    #         branch_id
    #         line:
    #
    #
    #     """
    #
    #     # vals['success_msg'] = success_msg
    #     # sale_order.action_confirm()
    #
    #     return request.redirect('/my/sale_order/%s' % sale_order.id)

    # @http.route(['/my/approval_requests/<int:approval_category_id>',
    #              '/my/approval_requests'], type='http',
    #             website=True, auth="user")
    # def approval_requests_list_view(self, approval_category_id=False):
    #     domain = [('request_owner_id', '=', request.env.user.id)]
    #     if approval_category_id:
    #         domain += [('category_id', '=', approval_category_id)]
    #     approval_requests = request.env['approval.request'].search(domain)
    #
    #     vals = {
    #         'approval_requests': approval_requests,
    #         'page_name': 'approval_requests',
    #         'approval_category_id': False,
    #     }
    #     if approval_category_id:
    #         vals.update({
    #             'approval_category_id': approval_category_id
    #         })
    #
    #     return request.render(
    #         'portal_approval_request.portal_my_approval_request_list', vals
    #     )
    #
    # def _get_custom_approval_category_url(self, category, request_id):
    #     """
    #     inherit to add custom url
    #     """
    #     return '/my/approval_requests/'
    #
    # @http.route(['/my/approval_requests/<int:approval_category_id>/'
    #              'request/<int:request_id>',
    #              '/my/approval_requests/request/<int:request_id>'], type='http',
    #             website=True, auth="user")
    # def approval_requests_form_view(self, approval_category_id=False, request_id=False):
    #     """
    #     get request id based on approval category
    #     """
    #     category = False
    #     if approval_category_id:
    #         category = request.env['approval.category'].browse(approval_category_id)
    #     elif request_id:
    #         if not category:
    #             category = request.env['approval.request'].browse(request_id).category_id
    #     if category and category.custom_approval_type not in ['none', False]:
    #         return self._get_custom_approval_category_url(category, request_id)
    #     approval_request = request.env['approval.request'].browse(request_id)
    #     if not approval_request.sudo().access_token:
    #         approval_request.sudo()._portal_ensure_token()
    #     approval_request.sudo().attachment_ids.generate_access_token()
    #     vals = {
    #         'approval_request': approval_request,
    #         'object': approval_request,
    #         'category': category,
    #         'page_name': 'approval_request_form_read'
    #     }
    #
    #     return request.render(
    #         'portal_approval_request.portal_my_approval_request_form_read', vals
    #     )
    #
    # @http.route(['/my/approval_request_category'],
    #             type='http', website=True)
    # def approval_request_kanban_view(self):
    #     approval_categories = request.env['approval.category'].search([])
    #
    #     vals = {
    #         'approval_categories': approval_categories,
    #         'page_name': 'approval_request_category',
    #     }
    #
    #     return request.render(
    #         'portal_approval_request.portal_approval_request_kanban', vals
    #     )
    #
    # @http.route(['/my/approval_request/new/<int:approval_request_id>'],
    #             type='http', website=True)
    # def request_approval_form_view(self, approval_request_id):
    #     approval_category = request.env['approval.category'].search([
    #         (
    #             'id',
    #             '=',
    #             approval_request_id
    #         )
    #     ])
    #     products = request.env['product.product'].search([
    #         (
    #             'company_id',
    #             'in',
    #             [http.request.env.user.company_id.id, False]
    #         )
    #     ])
    #     partner_id = request.env['res.partner'].sudo().search([
    #         (
    #             'company_id',
    #             'in',
    #             [http.request.env.user.company_id.id, False]
    #         ),
    #     ])
    #     vals = {
    #         'approval_category': approval_category,
    #         'partner_id': partner_id,
    #         'page_name': 'approval_request_new',
    #         'products': products,
    #     }
    #     return request.render(
    #         'portal_approval_request.portal_approval_request_form', vals
    #     )
    #
