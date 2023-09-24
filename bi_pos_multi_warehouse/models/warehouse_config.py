from odoo import api, fields, models, tools,_
import json
from odoo.exceptions import RedirectWarning, UserError, ValidationError ,Warning
from odoo.tools import float_is_zero, float_compare,format_datetime
from itertools import groupby

class WarehouseQty(models.Model):
    _inherit = 'stock.warehouse'

    quantity = fields.Integer('quantity')

class WarehouseStockQty(models.Model):
    _inherit = 'stock.quant'

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    warehouse_quantity = fields.Char(compute='_get_quantity_warehouse_location', string='Quantity per warehouse')
    quantity_warehouse = fields.Char('Warehouse Qty')

    @api.depends('product_id', 'location_id')
    def get_products_stock_location_qty(self, location, products):
        res = {}
        product_ids = self.env['product.product'].browse(products)
        for product in product_ids:

            quants = self.env['stock.quant'].search(
                [('product_id', '=', product.id), ('location_id', '=', location['id'])])
            if len(quants) > 1:
                quantity = 0.0
                for quant in quants:
                    quantity += quant.quantity
                res.update({product.id: quantity})
            else:
                res.update({product.id: quants.quantity})

        return [res]

    def _get_quantity_warehouse_location(self):
        for record in self:
            text = ''
            product_id = self.env['product.product'].sudo().search([('product_tmpl_id', '=', record.id)])
            if product_id:
                quant_ids = self.env['stock.quant'].sudo().search(
                    [('product_id', '=', product_id[0].id), ('location_id.usage', '=', 'internal')])
                res = {}
                for quant in quant_ids:
                    if quant.location_id:
                        if quant.location_id not in res:
                            res.update({quant.location_id: 0})
                        res[quant.location_id] += quant.quantity

                res1 = {}
                for location in res:
                    warehouse = False
                    location1 = location
                    while (not warehouse and location1):
                        warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', location1.id)])
                        if len(warehouse_id) > 0:
                            warehouse = True
                        else:
                            warehouse = False
                        location1 = location1.location_id
                    if warehouse_id:
                        if warehouse_id.name not in res1:
                            res1.update({warehouse_id.name: 0})
                        res1[warehouse_id.name] += res[location]

                for item in res1:
                    if res1[item] != 0:
                        text = text + item + ': ' + str(res1[item]) + " "
                record.warehouse_quantity = text

    def get_single_product(self, product, location1):
        res = []
        pro = self.env['product.product'].browse(product)
        quants = self.env['stock.quant'].search([('product_id', '=', pro.id), ('location_id', '=', location1['id'])])

        if len(quants) > 1:
            quantity = 0.0
            for quant in quants:
                quantity += quant.quantity
            res.append([pro.id, quantity])
        else:
            res.append([pro.id, quants.quantity])
        return res


    def warehouse_qty(self, warehouse, product, session):
        res = {}
        res2 = []
        for record in warehouse:
            if product:
                quant_ids = self.env['stock.quant'].sudo().search(
                    [('product_id', '=', product), ('location_id.usage', '=', 'internal')])
                product_obj = self.env["product.product"].browse(product)
                data = product_obj.with_context({'warehouse': record['id']})._get_report_data(
                    [product_obj.product_tmpl_id.id],
                    [product_obj.id]
                )
                if session == 'qty_available':
                    res[record['id']] = data['quantity_on_hand']
                if session == 'virtual_available':
                    res[record['id']] = data['virtual_available']

                res2.append({'quantity': res[record['id']], 'location': record['name'],'id':record['id']})
        return res2



class PosConfigLocationwarehouse(models.Model):
    _inherit = 'pos.config'

    def _get_default_location(self):
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)],
                                                  limit=1).lot_stock_id

    pos_stock = fields.Boolean(string='Display stock in pos', help='Allow display stock in pos.')
    default_location_src_id = fields.Many2one(
        'stock.location', 'Stock Location',
        check_company=True, default=_get_default_location)

    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses', 
                                     help="Show the routes that apply on selected warehouses." )
    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True, copy=False)
    location_id = fields.Many2one(
        comodel_name='stock.location',
        related='picking_id.location_id',
        string="Stock Location", store=True,
        readonly=True,
    )
    stock_qty = fields.Selection([('qty_available', 'Available Quantity'),
                                  ('virtual_available', 'Unreserved Quantity'),
                                  ], 'Stock Type')
    Ready_state = fields.Boolean(string='Set Picking In Ready State', help='Allow display stock in ready state pos.')
    Negative_selling = fields.Boolean(string='Allow POS Order When Product is Out of Stock', help='Allow negative selling in pos.')



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_stock = fields.Boolean(related='pos_config_id.pos_stock',string='Display stock in pos', help='Allow display stock in pos.',readonly=False)
    #default_location_src_id = fields.Many2one(related='pos_config_id.default_location_src_id',check_company=True, string='Stock Location',readonly=False)

    warehouse_ids = fields.Many2many(related='pos_config_id.warehouse_ids',string='Warehouses', 
                                     help="Show the routes that apply on selected warehouses." ,readonly=False)
    picking_id = fields.Many2one(related='pos_config_id.picking_id', string='Picking',  copy=False,readonly=False)
    location_id = fields.Many2one(
        related='pos_config_id.location_id', 
        string="Stock Location", store=True,
        readonly=False,
    )
    stock_qty = fields.Selection(related='pos_config_id.stock_qty', string='Stock Type',required=True,readonly=False)
    Ready_state = fields.Boolean(related='pos_config_id.Ready_state',string='Set Picking In Ready State', help='Allow display stock in ready state pos.',readonly=False)
    Negative_selling = fields.Boolean(related='pos_config_id.Negative_selling',string='Allow POS Order When Product is Out of Stock', help='Allow negative selling in pos.',readonly=False)




class PosOrderLinePicking(models.Model):
    _inherit = 'pos.order.line'

    stock_location_name = fields.Char('Warehouse')


class PosOrderPicking(models.Model):
    _inherit = 'pos.order'

    picking_ids = fields.One2many(
        'stock.picking', 'pos_id', string='Transfers',
        domain="[('state', 'in', ('done', 'cancel'))]",
        help='List of transfers associated to this pos')

    stock_location_name = fields.Char('Warehouse')


    def _create_order_picking(self):
        self.ensure_one()
        if not self.session_id.update_stock_at_closing or (self.company_id.anglo_saxon_accounting and self.to_invoice):
            config_id = self.session_id.config_id
            picking_type = self.config_id.picking_type_id

            if self.partner_id.property_stock_customer:
                destination_id = self.partner_id.property_stock_customer.id
            elif not picking_type or not picking_type.default_location_dest_id:
                destination_id = self.env['stock.warehouse']._get_partner_locations()[0].id
            else:
                destination_id = picking_type.default_location_dest_id.id

            different = self.lines.filtered(lambda l: l.stock_location_name)

            if different:
                for line in different:
                    picking_type = self.env['stock.picking.type'].search(
                        [('warehouse_id.name', '=', line.stock_location_name), ('code', '=', 'outgoing'),
                         ('sequence_code', '=', 'POS')])

                    diff_pick = self.env['stock.picking'].with_context(diff_loc=line.stock_location_name)._create_picking_from_pos_order_lines(destination_id, line, picking_type, self.partner_id, self.config_id)
                    diff_pick.write({'pos_session_id': self.session_id.id, 'pos_id': self.id,'pos_order_id': self.id, 'origin': self.name})


class PickingPosStock(models.Model):
    _inherit = 'stock.picking'

    pos_id = fields.Many2one('pos.order', 'Related POS')

    @api.model
    def _create_picking_from_pos_order_lines(self, location_dest_id, lines, picking_type, partner=False, config_id=False):
        """We'll create some picking based on order_lines"""

        pickings = self.env['stock.picking']

        stockable_lines = lines.filtered(
            lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty,
                                                                                      precision_rounding=l.product_id.uom_id.rounding))

        if not stockable_lines:
            return pickings
        positive_lines = stockable_lines.filtered(lambda l: l.qty > 0)
        negative_lines = stockable_lines - positive_lines

        if positive_lines:
            location_id = picking_type.default_location_src_id.id
            if self._context.get('diff_loc'):
                location_id = self._context.get('diff_loc')
            positive_picking = self.env['stock.picking'].create(
                self._prepare_picking_vals(partner, picking_type.id, picking_type.default_location_src_id.id, picking_type.default_location_dest_id.id)
            )
            positive_picking._create_move_from_pos_order_lines(positive_lines)
            try:
                with self.env.cr.savepoint():
                    if (not config_id.Ready_state):
                        positive_picking._action_done()
                    else:
                        positive_picking.write({
                            'state': 'assigned'
                        })
            except (UserError, ValidationError):
                pass

            pickings |= positive_picking

        if negative_lines:

            if picking_type.return_picking_type_id:
                return_picking_type = picking_type.return_picking_type_id
                return_location_id = return_picking_type.default_location_dest_id.id
            else:
                return_picking_type = picking_type
                return_location_id = picking_type.default_location_src_id.id

            negative_picking = self.env['stock.picking'].create(
                self._prepare_picking_vals(partner, picking_type.id, picking_type.default_location_dest_id.id, picking_type.default_location_src_id.id)
            )
            negative_picking._create_move_from_pos_order_lines(negative_lines)
            try:
                with self.env.cr.savepoint():
                    if (not config_id.Ready_state):
                        negative_picking._action_done()
                    else:
                        negative_picking.write({
                            'state': 'assigned'
                        })
            except (UserError, ValidationError):
                pass
            pickings |= negative_picking
        return pickings

    def _prepare_picking_vals(self, partner, picking_type, location_id, location_dest_id):
        return {
            'partner_id': partner.id if partner else False,
            'user_id': False,
            'picking_type_id': picking_type,
            'move_type': 'direct',
            'location_id': location_id,
            'location_dest_id': location_dest_id,
        }
    def _create_move_from_pos_order_lines(self, lines):
        self.ensure_one()
        lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: l.product_id.id)
        for product, lines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*lines)
            first_line = order_lines[0]
            current_move = self.env['stock.move'].create(
                self._prepare_stock_move_vals(first_line, order_lines)
            )

            confirmed_moves = current_move._action_confirm()
            for move in confirmed_moves:
                if first_line.product_id == move.product_id and first_line.product_id.tracking != 'none':
                    if self.picking_type_id.use_existing_lots or self.picking_type_id.use_create_lots:
                        for line in order_lines:
                            sum_of_lots = 0
                            for lot in line.pack_lot_ids.filtered(lambda l: l.lot_name):
                                if line.product_id.tracking == 'serial':
                                    qty = 1
                                else:
                                    qty = abs(line.qty)
                                ml_vals = move._prepare_move_line_vals()
                                ml_vals.update({'qty_done': qty})
                                if self.picking_type_id.use_existing_lots:
                                    existing_lot = self.env['stock.production.lot'].search([
                                        ('company_id', '=', self.company_id.id),
                                        ('product_id', '=', line.product_id.id),
                                        ('name', '=', lot.lot_name)
                                    ])
                                    if not existing_lot and self.picking_type_id.use_create_lots:
                                        existing_lot = self.env['stock.production.lot'].create({
                                            'company_id': self.company_id.id,
                                            'product_id': line.product_id.id,
                                            'name': lot.lot_name,
                                        })
                                    quant = existing_lot.quant_ids.filtered(
                                        lambda q: q.quantity > 0.0 or q.location_id.parent_path.startswith(
                                            move.location_id.parent_path))[-1:]
                                    ml_vals.update({
                                        'lot_id': existing_lot.id,
                                        'location_id': quant.location_id.id or move.location_id.id
                                    })
                                else:
                                    ml_vals.update({
                                        'lot_name': lot.lot_name,
                                    })
                                self.env['stock.move.line'].create(ml_vals)
                                sum_of_lots += qty
                            if abs(line.qty) != sum_of_lots:
                                difference_qty = abs(line.qty) - sum_of_lots
                                ml_vals = current_move._prepare_move_line_vals()
                                if line.product_id.tracking == 'serial':
                                    ml_vals.update({'qty_done': 1})
                                    for i in range(int(difference_qty)):
                                        self.env['stock.move.line'].create(ml_vals)
                                else:
                                    ml_vals.update({'qty_done': difference_qty})
                                    self.env['stock.move.line'].create(ml_vals)
                    else:
                        for move_line in move.move_line_ids:
                            move_line.qty_done = move_line.product_uom_qty
                        if float_compare(move.product_uom_qty, move.quantity_done,
                                         precision_rounding=move.product_uom.rounding) > 0:
                            remaining_qty = move.product_uom_qty - move.quantity_done
                            ml_vals = move._prepare_move_line_vals()
                            ml_vals.update({'qty_done': remaining_qty})
                            self.env['stock.move.line'].create(ml_vals)

                else:
                    if self.user_has_groups('stock.group_tracking_owner'):
                        move._action_assign()
                        for move_line in move.move_line_ids:
                            move_line.qty_done = move_line.product_uom_qty
                        if float_compare(move.product_uom_qty, move.quantity_done,
                                         precision_rounding=move.product_uom.rounding) > 0:
                            remaining_qty = move.product_uom_qty - move.quantity_done
                            ml_vals = move._prepare_move_line_vals()
                            ml_vals.update({'qty_done': remaining_qty})
                            self.env['stock.move.line'].create(ml_vals)

                    move.quantity_done = move.product_uom_qty


class Product(models.Model):
    _inherit = 'product.product'

    quant_ids = fields.One2many("stock.quant", "product_id", string="Quants",
                                domain=[('location_id.usage', '=', 'internal')])

    quant_text = fields.Text('Quant Qty', compute='_compute_avail_locations', store=True)

    @api.depends('stock_quant_ids', 'stock_quant_ids.product_id', 'stock_quant_ids.location_id',
                 'stock_quant_ids.quantity')
    def _compute_avail_locations(self):
        notifications = []
        for rec in self:
            final_data = {}
            rec.quant_text = json.dumps(final_data)
            if rec.type == 'product':
                quants = self.env['stock.quant'].sudo().search(
                    [('product_id', 'in', rec.ids), ('location_id.usage', '=', 'internal')])
                outgoing = self.env['stock.move'].sudo().search(
                    [('product_id', '=', rec.id), ('state', 'not in', ['done','cancel']),
                     ('location_id.usage', '=', 'internal'),
                     ('picking_id.picking_type_code', 'in', ['outgoing'])])
                incoming = self.env['stock.move'].sudo().search(
                    [('product_id', '=', rec.id), ('state', 'not in', ['done','cancel']),
                     ('location_dest_id.usage', '=', 'internal'),
                     ('picking_id.picking_type_code', 'in', ['incoming'])])
                for quant in quants:
                    loc = quant.location_id.id
                    if loc in final_data:
                        last_qty = final_data[loc][0]
                        final_data[loc][0] = last_qty + quant.quantity
                    else:
                        final_data[loc] = [quant.quantity, 0, 0]

                for out in outgoing:
                    loc = out.location_id.id
                    if loc in final_data:
                        last_qty = final_data[loc][1]
                        final_data[loc][1] = last_qty + out.product_qty
                    else:
                        final_data[loc] = [0, out.product_qty, 0]

                for inc in incoming:
                    loc = inc.location_dest_id.id
                    if loc in final_data:
                        last_qty = final_data[loc][2]
                        final_data[loc][2] = last_qty + inc.product_qty
                    else:
                        final_data[loc] = [0, 0, inc.product_qty]

                rec.quant_text = json.dumps(final_data)
        return True

class PosStockSession(models.Model):
    _inherit ='pos.session'



    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        new_model = 'stock.warehouse'
        if new_model not in result:
            result.append(new_model)
        new_model='stock.location'
        if new_model not in result:
            result.append(new_model)
        return result


    def _loader_params_stock_location(self):
        return {
            'search_params': {
                'domain': [], 
                'fields': []
            }
        }




    def _loader_params_stock_warehouse(self):
        return {
            'search_params': {
                'domain': [('id', 'in', self.config_id.warehouse_ids.ids)], 
                'fields': ['id','name']
            }
        }


    def _get_pos_ui_stock_warehouse(self, params):
        return self.env['stock.warehouse'].search_read(**params['search_params'])

    def _get_pos_ui_stock_location(self, params):
        return self.env['stock.location'].search_read(**params['search_params'])
        




    def _loader_params_product_product(self):
        res = super(PosStockSession, self)._loader_params_product_product()
        fields = res.get('search_params').get('fields')
        fields.extend(['type','quant_text','qty_available','incoming_qty','outgoing_qty','virtual_available','name'])
        res['search_params']['fields'] = fields
        return res


    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        prods = {}
        for rec in loaded_data['product.product'] :
            prods[rec['id']]=rec['quant_text']
        loaded_data['prod_with_quant'] = prods
        loc_by_id={}
        for rec in loaded_data['stock.warehouse']:
            loc_by_id[rec['id']]=rec
        loaded_data['pos_custom_location'] = loaded_data['stock.warehouse']
        loaded_data['loc_by_id'] = loc_by_id
        locations=[]
        for rec in loaded_data['stock.location']:
            if rec['warehouse_id'] and rec['warehouse_id'][0] in self.config_id.warehouse_ids.ids:
                locations.append(rec)
        loaded_data['locations'] = locations
        


    def _create_picking_at_end_of_session(self):
        self.ensure_one()
        lines_grouped_by_dest_location = {}
        picking_type = self.config_id.picking_type_id

        if not picking_type or not picking_type.default_location_dest_id:
            session_destination_id = self.env['stock.warehouse']._get_partner_locations()[0].id
        else:
            session_destination_id = picking_type.default_location_dest_id.id

        for order in self.order_ids:
            picking_type = order.config_id.picking_type_id

            if order.partner_id.property_stock_customer:
                destination_id = order.partner_id.property_stock_customer.id
            elif not picking_type or not picking_type.default_location_dest_id:
                destination_id = order.env['stock.warehouse']._get_partner_locations()[0].id
            else:
                destination_id = picking_type.default_location_dest_id.id

            different = order.lines.filtered(lambda l: l.stock_location_name)

            if different:
                for line in different:
                    picking_type = order.env['stock.picking.type'].search(
                        [('warehouse_id.name', '=', line.stock_location_name), ('code', '=', 'outgoing'),
                         ('sequence_code', '=', 'POS')])

                    diff_pick = order.env['stock.picking'].with_context(
                        diff_loc=line.stock_location_name)._create_picking_from_pos_order_lines(destination_id, line,
                                                                                                picking_type,
                                                                                                order.partner_id,
                                                                                                order.config_id)
                    diff_pick.write({'pos_session_id': order.session_id.id, 'pos_id': order.id, 'pos_order_id': order.id,
                                     'origin': order.name})


class ProductTemplate(models.Model):
    _inherit = "product.template"

    warehouse_quantity = fields.Char(compute='_get_quantity_warehouse_location', string='Quantity per warehouse')
    warehouse_id = fields.Many2one(compute='_get_quantity_warehouse_forcast_location', string='Quantity per warehouse')


    def _get_quantity_warehouse_location(self):
        for record in self:
            text = ''
            product_id = self.env['product.product'].sudo().search([('product_tmpl_id', '=', record.id)])
            if product_id:
                quant_ids = self.env['stock.quant'].sudo().search([('product_id','=',product_id[0].id),('location_id.usage','=','internal')])
                res = {}
                for quant in quant_ids:
                    if quant.location_id:
                        if quant.location_id not in res:
                            res.update({quant.location_id:0})
                        res[quant.location_id] += quant.quantity

                res1 = {}
                for location in res:
                    warehouse = False
                    location1 = location
                    while (not warehouse and location1):
                        warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',location1.id)])
                        if len(warehouse_id) > 0:
                            warehouse = True
                        else:
                            warehouse = False
                        location1 = location1.location_id
                    if warehouse_id:
                        if warehouse_id.name not in res1:
                            res1.update({warehouse_id.name:0})
                        res1[warehouse_id.name] += res[location]

                for item in res1:
                    if res1[item] != 0:
                        text = text + item + ': ' + str(res1[item])
                record.warehouse_quantity = text


    def _get_quantity_warehouse_forcast_location(self):
        for record in self:
            text = ''
            product_id = self.env['product.product'].sudo().search([('product_tmpl_id', '=', record.id)])
            if product_id:
                quant_ids = self.env['stock.quant'].sudo().search([('product_id','=',product_id[0].id),('location_id.usage','=','internal')])
                res = {}
                for quant in quant_ids:
                    if quant.location_id:
                        if quant.location_id not in res:
                            res.update({quant.location_id:0})
                        res[quant.location_id] += quant.virtual_available

                res1 = {}
                for location in res:
                    warehouse = False
                    location1 = location
                    while (not warehouse and location1):
                        warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',location1.id)])
                        if len(warehouse_id) > 0:
                            warehouse = True
                        else:
                            warehouse = False
                        location1 = location1.location_id
                    if warehouse_id:
                        if warehouse_id.name not in res1:
                            res1.update({warehouse_id.name:0})
                        res1[warehouse_id.name] += res[location]

                for item in res1:
                    if res1[item] != 0:
                        text = text + item + ': ' + str(res1[item])
                record.warehouse_quantity = text





