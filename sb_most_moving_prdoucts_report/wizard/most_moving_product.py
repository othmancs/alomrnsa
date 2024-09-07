from odoo import fields, models
from datetime import datetime


class ProductWizard(models.TransientModel):
    _name = 'most.moving.product.wizard'

    branch_id = fields.Many2one('res.branch', string="الفــرع", required=True)
    product_category_ids = fields.Many2many('product.category', string="فئه المنج", required=True)
    date_from = fields.Date(string="مـن تـاريـخ", required=True)
    date_to = fields.Date(string="إلـى تـاريـخ", required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
    printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
    print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)

    def _compute_printed_by(self):
        for record in self:
            record.printed_by = self.env.user.name

    def pdf_report_action(self):
        # Convert dates to date objects for comparison
        date_from = fields.Date.to_date(self.date_from)
        date_to = fields.Date.to_date(self.date_to)

        # Prepare domain for stock.move.line
        domain = [('state', '=', 'done')]
        moves = self.env['stock.move.line'].search(domain)

        # Extract product IDs from the moves
        product_ids_in_moves = moves.mapped('product_id.id')

        # partner_customers_location = 5  # Assuming 5 is the ID for 'Partners/Customers'
        partner_customers_location = self.env['stock.location'].browse(5)
        print("Found location:", partner_customers_location.name)

        warehouses = self.env['stock.warehouse'].search([('branch_id', '=', self.branch_id.id)])
        warehouse_ids = warehouses.mapped('lot_stock_id.id')
        print("Warehouse IDs:", warehouse_ids)

        # Collect product data
        product_data = []
        for category in self.product_category_ids:
            products = self.env['product.product'].search([
                ('categ_id', '=', category.id),
                ('id', 'in', product_ids_in_moves)
            ])
            for product in products:
                # Filter moves for the product and branch
                product_moves = moves.filtered(lambda m: m.product_id == product and m.branch_id == self.branch_id)
                print("product_moves=======>", product_moves)

                # Ensure m.date is a date object
                beginning_balance_incoming_moves = product_moves.filtered(
                    lambda m: m.date.date() < date_from and m.picking_code == 'incoming')
                print("beginning_balance_incoming_moves=======>", beginning_balance_incoming_moves)

                beginning_balance_outgoing_moves = product_moves.filtered(
                    lambda m: m.date.date() < date_from and m.picking_code == 'outgoing')
                print("beginning_balance_outgoing_moves=======>", beginning_balance_outgoing_moves)

                # Sum quantities for incoming and outgoing moves
                beginning_balance_incoming = sum(beginning_balance_incoming_moves.mapped('qty_done'))
                print('sum beginning_balance_incoming====>', beginning_balance_incoming)
                beginning_balance_outgoing = sum(beginning_balance_outgoing_moves.mapped('qty_done'))
                print('sum beginning_balance_outgoing====>', beginning_balance_outgoing)
                # Calculate beginning balance
                beginning_balance = beginning_balance_incoming - beginning_balance_outgoing
                print("beginning_balance=======>", beginning_balance)

                # Calculate incoming_period and outgoing_period
                incoming_period = sum(product_moves.filtered(
                    lambda m: date_from <= m.date.date() <= date_to and m.picking_code == 'incoming').mapped(
                    'qty_done'))
                print("incoming_period=======>", incoming_period)

                outgoing_period = sum(product_moves.filtered(
                    lambda m: date_from <= m.date.date() <= date_to and m.picking_code == 'outgoing').mapped(
                    'qty_done'))
                print("outgoing_period=======>", outgoing_period)

                # # Calculate available quantity
                # available_qty = (beginning_balance + incoming_period) - outgoing_period
                # print("available_qty=======>", available_qty)

                # Calculate additional quantity for location 'Partners/Customers' and picking code 'incoming'
                return_qty = sum(product_moves.filtered(
                    lambda
                        m: date_from <= m.date.date() <= date_to and m.location_id == partner_customers_location and m.picking_code == 'incoming').mapped(
                    'qty_done'))
                print("return_qty=======>", return_qty)

                # Handle 'internal' picking codes
                product_moves_internal = moves.filtered(
                    lambda m: m.product_id == product and m.picking_code == 'internal')

                print("product_moves_internal=======>", product_moves_internal)
                for rec in product_moves_internal:
                    print("rec.qty=======>", rec.qty_done)
                    print("rec.location_dest_id.id=======>", rec.location_dest_id.name)
                    print("rec.location_dest_id.id=======>", rec.location_dest_id.id)
                    print("rec.location_id.id=======>", rec.location_id.id)
                    print("warehouse_ids=======>", warehouse_ids)
                    print("warehouse_ids in warehouse_ids=======>", rec.location_dest_id.id in warehouse_ids)
                    print("warehouse_ids in warehouse_ids=======>", rec.location_id.id in warehouse_ids)

                # Calculate internal incoming and outgoing
                internal_incoming = sum(product_moves_internal.filtered(
                    lambda m: date_from <= m.date.date() <= date_to and m.location_dest_id.id in warehouse_ids).mapped(
                    'qty_done'))
                print("internal_incoming=======>", internal_incoming)

                # incoming_period += internal_incoming
                internal_outgoing = sum(product_moves_internal.filtered(
                    lambda m: date_from <= m.date.date() <= date_to and m.location_id.id in warehouse_ids).mapped(
                    'qty_done'))
                # outgoing_period += internal_outgoing
                print("internal_outgoing=======>", internal_outgoing)

                internal_beginning_balance = sum(product_moves_internal.filtered(
                    lambda m: m.date.date() < date_from and m.location_dest_id.id in warehouse_ids).mapped('qty_done'))
                print("internal_beginning_balance=======>", internal_beginning_balance)

                ##================================================================
                new_incoming = (internal_incoming + incoming_period) - return_qty
                print("new_incoming=======>", new_incoming)
                new_outgoing = outgoing_period + internal_outgoing
                print('new_outging======>', new_outgoing)

                new_beginning_balance = beginning_balance + internal_beginning_balance
                print('new_beginning_balance======>', new_beginning_balance)
                # Calculate available quantity
                available_qty = (new_beginning_balance + new_incoming + return_qty) - new_outgoing
                print("available_qty=======>", available_qty)

                sales_percentage = 0
                if new_incoming != 0 and new_outgoing != 0:
                    sales_percentage = (new_outgoing / new_incoming) * 100

                elif new_incoming == 0 and new_outgoing == 0:
                    sales_percentage = 0

                elif new_outgoing == 0:
                    sales_percentage = 0
                else:
                    sales_percentage = 100

                if (beginning_balance != 0 or incoming_period != 0 or outgoing_period != 0 or
                        available_qty != 0 or return_qty != 0 or internal_incoming != 0 or internal_outgoing != 0):
                    product_data.append({
                        'product_reference': product.default_code,
                        'product_description': product.name,
                        'beginning_balance': new_beginning_balance,
                        'available_qty': available_qty,
                        'return_qty': return_qty,
                        'internal_incoming': internal_incoming,
                        'internal_outgoing': internal_outgoing,
                        'new_incoming': new_incoming,
                        'new_outgoing': new_outgoing,
                        'sales_percentage': sales_percentage,
                    })

        wizard_data = self.read()[0]
        wizard_data['products'] = product_data
        data = {
            'form': wizard_data,
        }

        print("product_data=======>", product_data)

        return self.env.ref("sb_most_moving_prdoucts_report.most_moving_product_report").report_action(self, data=data)

    def xls_report_action(self):
        # Convert dates to date objects for comparison
        date_from = fields.Date.to_date(self.date_from)
        date_to = fields.Date.to_date(self.date_to)

        # Prepare domain for stock.move.line
        domain = [('state', '=', 'done')]
        moves = self.env['stock.move.line'].search(domain)

        # Extract product IDs from the moves
        product_ids_in_moves = moves.mapped('product_id.id')

        # partner_customers_location = 5  # Assuming 5 is the ID for 'Partners/Customers'
        partner_customers_location = self.env['stock.location'].browse(5)
        print("Found location:", partner_customers_location.name)

        warehouses = self.env['stock.warehouse'].search([('branch_id', '=', self.branch_id.id)])
        warehouse_ids = warehouses.mapped('lot_stock_id.id')
        print("Warehouse IDs:", warehouse_ids)

        # Collect product data
        product_data = []
        for category in self.product_category_ids:
            products = self.env['product.product'].search([
                ('categ_id', '=', category.id),
                ('id', 'in', product_ids_in_moves)
            ])
            for product in products:
                # Filter moves for the product and branch
                product_moves = moves.filtered(lambda m: m.product_id == product and m.branch_id == self.branch_id)
                print("product_moves=======>", product_moves)

                # Ensure m.date is a date object
                beginning_balance_incoming_moves = product_moves.filtered(
                    lambda m: m.date.date() < date_from and m.picking_code == 'incoming')
                print("beginning_balance_incoming_moves=======>", beginning_balance_incoming_moves)

                beginning_balance_outgoing_moves = product_moves.filtered(
                    lambda m: m.date.date() < date_from and m.picking_code == 'outgoing')
                print("beginning_balance_outgoing_moves=======>", beginning_balance_outgoing_moves)

                # Sum quantities for incoming and outgoing moves
                beginning_balance_incoming = sum(beginning_balance_incoming_moves.mapped('qty_done'))
                print('sum beginning_balance_incoming====>', beginning_balance_incoming)
                beginning_balance_outgoing = sum(beginning_balance_outgoing_moves.mapped('qty_done'))
                print('sum beginning_balance_outgoing====>', beginning_balance_outgoing)
                # Calculate beginning balance
                beginning_balance = beginning_balance_incoming - beginning_balance_outgoing
                print("beginning_balance=======>", beginning_balance)

                # Calculate incoming_period and outgoing_period
                incoming_period = sum(product_moves.filtered(
                    lambda m: date_from <= m.date.date() <= date_to and m.picking_code == 'incoming').mapped(
                    'qty_done'))
                print("incoming_period=======>", incoming_period)

                outgoing_period = sum(product_moves.filtered(
                    lambda m: date_from <= m.date.date() <= date_to and m.picking_code == 'outgoing').mapped(
                    'qty_done'))
                print("outgoing_period=======>", outgoing_period)

                # # Calculate available quantity
                # available_qty = (beginning_balance + incoming_period) - outgoing_period
                # print("available_qty=======>", available_qty)

                # Calculate additional quantity for location 'Partners/Customers' and picking code 'incoming'
                return_qty = sum(product_moves.filtered(
                    lambda
                        m: date_from <= m.date.date() <= date_to and m.location_id == partner_customers_location and m.picking_code == 'incoming').mapped(
                    'qty_done'))
                print("return_qty=======>", return_qty)

                # Handle 'internal' picking codes
                product_moves_internal = moves.filtered(
                    lambda m: m.product_id == product and m.picking_code == 'internal')
                print("product_moves_internal=======>", product_moves_internal)
                for rec in product_moves_internal:
                    print("rec.qty=======>", rec.qty_done)
                    print("rec.location_dest_id.id=======>", rec.location_dest_id.name)
                    print("rec.location_dest_id.id=======>", rec.location_dest_id.id)
                    print("rec.location_id.id=======>", rec.location_id.id)
                    print("warehouse_ids=======>", warehouse_ids)
                    print("warehouse_ids in warehouse_ids=======>", rec.location_dest_id.id in warehouse_ids)
                    print("warehouse_ids in warehouse_ids=======>", rec.location_id.id in warehouse_ids)

                # Calculate internal incoming and outgoing
                internal_incoming = sum(product_moves_internal.filtered(
                    lambda m: date_from <= m.date.date() <= date_to and m.location_dest_id.id in warehouse_ids).mapped(
                    'qty_done'))
                print("internal_incoming=======>", internal_incoming)

                # incoming_period += internal_incoming
                internal_outgoing = sum(product_moves_internal.filtered(
                    lambda m: date_from <= m.date.date() <= date_to and m.location_id.id in warehouse_ids).mapped(
                    'qty_done'))
                # outgoing_period += internal_outgoing
                print("internal_outgoing=======>", internal_outgoing)

                internal_beginning_balance = sum(product_moves_internal.filtered(
                    lambda m: m.date.date() < date_from and m.location_dest_id.id in warehouse_ids).mapped('qty_done'))
                print("internal_beginning_balance=======>", internal_beginning_balance)

                ##================================================================
                new_incoming = internal_incoming + incoming_period
                print("new_incoming=======>", new_incoming)
                new_outgoing = outgoing_period + internal_outgoing
                print('new_outging======>', new_outgoing)

                new_beginning_balance = beginning_balance + internal_beginning_balance
                print('new_beginning_balance======>', new_beginning_balance)
                # Calculate available quantity
                available_qty = (new_beginning_balance + new_incoming) - new_outgoing
                print("available_qty=======>", available_qty)

                sales_percentage = 0
                if new_incoming != 0 and new_outgoing != 0:
                    sales_percentage = (new_outgoing / new_incoming) * 100

                elif new_incoming == 0 and new_outgoing == 0:
                    sales_percentage = 0

                elif new_outgoing == 0:
                    sales_percentage = 0
                else:
                    sales_percentage = 100

                if (beginning_balance != 0 or incoming_period != 0 or outgoing_period != 0 or
                        available_qty != 0 or return_qty != 0 or internal_incoming != 0 or internal_outgoing != 0):
                    product_data.append({
                        'product_reference': product.default_code,
                        'product_description': product.name,
                        'beginning_balance': new_beginning_balance,
                        # 'incoming_period': incoming_period,
                        # 'outgoing_period': outgoing_period,
                        'available_qty': available_qty,
                        'return_qty': return_qty,
                        'internal_incoming': internal_incoming,
                        'internal_outgoing': internal_outgoing,
                        'new_incoming': new_incoming,
                        'new_outgoing': new_outgoing,
                        'sales_percentage': sales_percentage,
                    })

        wizard_data = self.read()[0]
        wizard_data['products'] = product_data
        data = {
            'form': wizard_data,
        }

        print("product_data=======>", product_data)

        return self.env.ref("sb_most_moving_prdoucts_report.most_moving_product_report_xls").report_action(self,
                                                                                                           data=data)

# from odoo import fields, models
# from datetime import datetime
#
#
# class ProductWizard(models.TransientModel):
#     _name = 'most.moving.product.wizard'
#
#     branch_id = fields.Many2one('res.branch', string="الفــرع", required=True)
#     product_category_ids = fields.Many2many('product.category', string="فئه المنج", required=True)
#     date_from = fields.Date(string="مـن تـاريـخ", required=True)
#     date_to = fields.Date(string="إلـى تـاريـخ", required=True)
#     company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company.id)
#     printed_by = fields.Char(string="طبع بواسطة", compute="_compute_printed_by")
#     print_date = fields.Date(string="تاريخ الطباعة", default=fields.Date.context_today)
#
#     def _compute_printed_by(self):
#         for record in self:
#             record.printed_by = self.env.user.name
#
#     def pdf_report_action(self):
#         # Convert dates to date objects for comparison
#         date_from = fields.Date.to_date(self.date_from)
#         date_to = fields.Date.to_date(self.date_to)
#         print("Converted date_from:", date_from)
#         print("Converted date_to:", date_to)
#
#         # Prepare domain for stock.move.line
#         domain = [('state', '=', 'done')]
#         # ('branch_id', '=', self.branch_id.id),
#         moves = self.env['stock.move.line'].search([('state', '=', 'done')])
#
#         # Extract product IDs from the moves
#         product_ids_in_moves = moves.mapped('product_id.id')
#
#         # partner_customers_location_id = 5  # Assuming 5 is the ID for 'Partners/Customers'
#         partner_customers_location = self.env['stock.location'].browse(5)
#         print("Found location:", partner_customers_location.name)
#
#         # Collect product data
#         product_data = []
#         for category in self.product_category_ids:
#             products = self.env['product.product'].search([
#                 ('categ_id', '=', category.id),
#                 ('id', 'in', product_ids_in_moves)
#             ])
#             for product in products:
#                 # Filter moves for the product and branch
#                 product_moves = moves.filtered(lambda m: m.product_id == product and m.branch_id == self.branch_id)
#                 print("product_moves=======>", product_moves)
#
#                 # Ensure m.date is a date object
#                 beginning_balance_incoming_moves = product_moves.filtered(
#                     lambda m: m.date.date() < date_from and m.picking_code == 'incoming')
#                 print("beginning_balance_incoming_moves=======>", beginning_balance_incoming_moves)
#                 beginning_balance_outgoing_moves = product_moves.filtered(
#                     lambda m: m.date.date() < date_from and m.picking_code == 'outgoing')
#                 print("beginning_balance_outgoing_moves=======>", beginning_balance_outgoing_moves)
#
#                 # Sum quantities for incoming and outgoing moves
#                 beginning_balance_incoming = sum(beginning_balance_incoming_moves.mapped('qty_done'))
#                 beginning_balance_outgoing = sum(beginning_balance_outgoing_moves.mapped('qty_done'))
#
#                 # Calculate beginning balance
#                 beginning_balance = beginning_balance_incoming - beginning_balance_outgoing
#                 print("beginning_balance=======>", beginning_balance)
#
#                 # Calculate incoming_period and outgoing_period
#                 incoming_period = sum(product_moves.filtered(
#                     lambda m: date_from <= m.date.date() <= date_to and m.picking_code == 'incoming').mapped(
#                     'qty_done'))
#                 print("incoming_period=======>", incoming_period)
#
#                 outgoing_period = sum(product_moves.filtered(
#                     lambda m: date_from <= m.date.date() <= date_to and m.picking_code == 'outgoing').mapped(
#                     'qty_done'))
#                 print("outgoing_period=======>", outgoing_period)
#
#                 # Calculate available quantity
#                 available_qty = beginning_balance + incoming_period - outgoing_period
#                 print("available_qty=======>", available_qty)
#
#                 # Calculate additional quantity for location 'Partners/Customers' and picking code 'incoming'
#                 return_qty = sum(product_moves.filtered(
#                     lambda m: m.location_id == partner_customers_location and m.picking_code == 'incoming').mapped(
#                     'qty_done'))
#                 print("return_qty=======>", return_qty)
#
#                 # =========================================================================================================
#                 product_moves_internal = moves.filtered(lambda m: m.product_id == product)
#                 print("product_moves_internal=======>", product_moves_internal)
#                 # Calculate incoming_period and outgoing_period
#                 internal_incoming = sum(product_moves_internal.filtered(
#                     lambda
#                         m: date_from <= m.date.date() <= date_to and m.picking_code == 'internal' and m.location_dest_id.branch_id.id == self.branch_id.id).mapped(
#                     'qty_done'))
#                 incoming_period += internal_incoming
#                 print("internal_incoming=======>", internal_incoming)
#
#                 internal_outgoing = sum(product_moves_internal.filtered(
#                     lambda
#                         m: date_from <= m.date.date() <= date_to and m.picking_code == 'internal' and m.location_id.branch_id.id == self.branch_id.id).mapped(
#                     'qty_done'))
#                 outgoing_period += internal_outgoing
#                 print("internal_outgoing=======>", internal_outgoing)
#                 # Append data
#                 product_data.append({
#                     'product_reference': product.default_code,
#                     'product_description': product.name,
#                     'beginning_balance': beginning_balance,
#                     'incoming_period': incoming_period,
#                     'outgoing_period': outgoing_period,
#                     'available_qty': available_qty,
#                     'return_qty': return_qty,
#                 })
#
#         wizard_data = self.read()[0]
#         wizard_data['products'] = product_data
#         data = {
#             'form': wizard_data,
#         }
#
#         print("product_data=======>", product_data)
#         print(
#             "================================================================================================================")
#
#         # Return the report action if applicable
#         return self.env.ref("sb_most_moving_prdoucts_report.most_moving_product_report").report_action(self, data=data)
#
#     def xls_report_action(self):
#         print("inside xls file")
#         # domain = []
#         # branch_ids = self.branch_ids
#         # if branch_ids:
#         #     domain += [('branch_id', 'in', branch_ids.ids)]
#         # date_from = self.date_from
#         # if date_from:
#         #     domain += [('date_order', '>=', date_from)]
#         # date_to = self.date_to
#         # if date_to:
#         #     domain += [('date_order', '<=', date_to)]
#         #
#         # domain += [('company_id', '=', self.company_id.id)]
#         #
#         # wizard_data = self.read()[0]
#         #
#         # branches = self.env['res.branch'].browse(wizard_data['branch_ids'])
#         # branch_dicts = [{'branch_name': name.name} for name in branches]
#         #
#         # wizard_data['branch_names'] = branch_dicts
#         #
#         # sale_orders = self.env['sale.order'].search_read(domain)
#         #
#         # data = {
#         #     'form': wizard_data,
#         # }
#         # return self.env.ref("sb_sale_order_report.sale_order_report_xls").report_action(self, data=data)
