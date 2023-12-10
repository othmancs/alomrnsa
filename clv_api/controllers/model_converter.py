from odoo.addons.stock.models.product import ProductTemplate, Product
from odoo.api import Environment
from .common_utils import CommonUtils

FOLDER_ID_PREFIX = 'folder_'


class ModelConverter:
    """
    Routins to convert Inventory API models from odoo's and vice versa
    """
    cutils = CommonUtils()

    def is_product_id_folder(self, product_id: str) -> bool:
        """
        True if passed string is virtual folder id (product with variants)
        @param product_id: folder or product id
        @return:
        """
        return product_id and product_id.startswith(FOLDER_ID_PREFIX)

    def get_template_id_from_folder_id(self, folder_id: str) -> str:
        """
        Returns product template id from folder id (empty string if it is not folder id)
        @param folder_id:
        @return:
        """
        if not self.is_product_id_folder(folder_id):
            return ''
        return folder_id[len(FOLDER_ID_PREFIX):]

    def product_template_to_inventory_item(self, env: Environment, prod_tmpl: ProductTemplate):
        """
        Converts product template object to the InventoryItem object
        @param env:
        @param prod_tmpl:
        @return:
        """
        if prod_tmpl.product_variant_count == 1:
            return self.product_to_inventory_item(env, prod_tmpl.product_variant_ids[0])
        else:
            return {
                'id': FOLDER_ID_PREFIX + str(prod_tmpl.id),
                'name': prod_tmpl.name,
                'barcode': prod_tmpl.barcode or "",
                'isFolder': True,
                'unitOfMeasureId': str(prod_tmpl.uom_id.id),
            }

    def product_to_inventory_item(self, env: Environment, prod: Product):
        """
        Converts product object ot the InventoryItem object
        @param env:
        @param prod:
        @return:
        """
        return self._clear_output_dict({
            'id': str(prod.id),
            'name': self._get_product_name(prod),
            'barcode': prod.barcode or "",
            'isFolder': False,
            'withSerialNumber': prod.product_tmpl_id.tracking == 'serial',
            'withSeries': prod.product_tmpl_id.tracking == 'lot',
            'seriesKey': str(prod.id),
            'unitOfMeasureId': str(prod.uom_id.id),
        })

    def product_to_related_data(self, env: Environment, prod: Product):
        """
        Create related data from the product (fills only unit of measure array)
        @param env:
        @param prod:
        @return:
        """
        return {'unitOfMeasure': self.product_to_unit_of_measure(env, prod)}

    def product_to_unit_of_measure(self, env: Environment, prod: Product):
        """
        Converts base uom of the product to UnitOfMeasure object
        @param env:
        @param prod:
        @return:
        """
        packaging = []
        if prod.uom_id:
            packaging.append({
                'id': str(prod.uom_id.id),
                'inventoryItemId': str(prod.id),
                'name': prod.uom_id.name,
                'unitsQuantity': 1,
                'price': 1 * prod.lst_price,
                'stockQuantity': prod.qty_available,
            })
        return packaging

    def product_template_to_related_data(self, env: Environment, prod_tmpl: ProductTemplate):
        """
        Converts product template to related data (array of unit of measures)
        @param env:
        @param prod_tmpl:
        @return:
        """
        return {'unitOfMeasure': self.product_template_to_unit_of_measure(env, prod_tmpl)}

    def product_template_to_unit_of_measure(self, env: Environment, prod_tmpl: ProductTemplate):
        """
        Converts product template to UnitOfMeasure object
        @param env:
        @param prod_tmpl:
        @return:
        """
        if prod_tmpl.product_variant_count == 1:
            return self.product_to_unit_of_measure(env, prod_tmpl.product_variant_ids[0])
        return []

    def stock_picking_to_doc_description(self, pick, document_type_name):
        """
        Fills InventoryAPI Document (header) object from the odoo stock.picking
        @param pick: odoo document
        @param document_type_name: the type of the Inventory API document
        @return:
        """
        vals = {}
        if pick:
            vals.update({
                'id': self.clear_to_str(pick.id),
                'name': self.clear_to_str(pick.name),
                # 'appointment': self._get_prop(pick, 'user_id', 'id'),
                'documentTypeName': document_type_name,
                'createDate': self.clear_to_str(pick.create_date),
                'modifiedDate': self.clear_to_str(pick.write_date),
                'finishedDate': self.clear_to_str(pick.date_done),
                'barcode': self.clear_to_str(pick.name),
                # 'priority': pick.priority,
                # 'description': self._clear_to_str(pick.description),
                'distributeByBarcode': True,
                'autoAppointed': False,
                'checkLocations': False,
                'customerVendorId': self._get_prop(pick, 'partner_id', 'id'),
                'customerVendorName': self._get_prop(pick, 'partner_id', 'name'),
                'scanLocations': self._stock_picking_get_scan_locations(pick),
                'scanInUnits': False,
                'warehouseExternalId': self._get_prop(pick, 'picking_type_id', 'warehouse_id', 'id'),
                'warehouseName': self._get_prop(pick, 'picking_type_id', 'warehouse_id', 'name')
            })
        return self._clear_output_dict(vals)

    def _stock_picking_get_scan_locations(self, pick):
        """
        True if we need to scan locations on mobile device
        """
        if not pick.env.user.has_group('stock.group_stock_multi_locations'):
            return False

        doc_type = self.cutils.get_document_type_info_by_document(pick)
        if doc_type.can_ignore_scan_locations:
            route = self.cutils.get_warehouse_route_steps_by_doc(pick.env, pick)
            if route == "two_steps" or route == "pick_ship":
                return False

        if not self._if_warehouse_contains_locations(pick):
            return False

        return pick.scan_locations

    def _if_warehouse_contains_locations(self, pick):
        """
        True if document location contains any children, False otherwise
        """
        doc_location = self.cutils.get_doc_main_location(pick)
        child_location_filter = []
        self.cutils.append_company_filter(child_location_filter, pick.company_id.id)
        child_location_filter.append(('complete_name', '=like', doc_location.complete_name + '/%'))
        return len(pick.env['stock.location'].search(child_location_filter, limit=1)) == 1

    def stock_picking_to_actual_lines(self, pick, ignore_zero_done: bool):
        """
        Converts stock.picking document to actual lines array (InventoryAPI object)
        @param pick: stock.oicking document
        @param ignore_zero_done: ignore zero qty_done lines or not
        @return:
        """
        vals = []
        if not pick:
            return vals
        if not pick.move_line_ids_without_package:
            return vals
        for line in pick.move_line_ids_without_package:
            if ignore_zero_done and line.qty_done <= 0:
                continue
            line_product = line.product_id
            adding_line = {
                'uid': self.clear_to_str(line.id),
                'bindedDocumentLineUid': self.clear_to_str(line.move_id.id),
                'inventoryItemId': self.clear_to_str(line_product.id),
                'expectedQuantity': self.clear_to_str(line.move_id.product_uom_qty),
                'actualQuantity': self.clear_to_str(line.qty_done),
                'unitOfMeasureId': self._get_prop(line_product, 'uom_id', 'id'),
                'inventoryItemName': line_product.name,
                'inventoryItemBarcode': self.clear_to_str(line_product.barcode),
                'unitOfMeasureName': self._get_prop(line_product, 'uom_id', 'name'),
                'registrationDate': self.clear_to_str(line_product.create_date),
                'documentId': self.clear_to_str(line.picking_id.id),
                'lastChangeDate': self.clear_to_str(line.write_date),
                'price': self.clear_to_str(line.product_id.lst_price),
                'purchasePrice': self.clear_to_str(line.product_id.standard_price),
                'sourceDocumentId': line.picking_id.origin,
            }
            if line_product.product_tmpl_id.tracking == 'serial':
                if line.lot_id:
                    adding_line['serialNumber'] = self.clear_to_str(line.lot_id.name)
                else:
                    adding_line['serialNumber'] = self.clear_to_str(line.lot_name)
            elif line_product.product_tmpl_id.tracking == 'lot':
                if line.lot_id:
                    adding_line['lot'] = self.clear_to_str(line.lot_id.name)
                else:
                    adding_line['lot'] = self.clear_to_str(line.lot_name)

            vals.append(self._clear_output_dict(adding_line))
        return vals

    def stock_picking_to_expected_lines(self, pick):
        """
        Converts stock.picking odoo object to expected lines (InventoryAPI)
        @param pick:
        @return:
        """
        vals = []
        if not pick:
            return vals
        if not pick.move_ids_without_package:
            return vals
        for line in pick.move_ids_without_package:
            line_product = line.product_id
            vals.append(self._clear_output_dict({
                'uid': self.clear_to_str(line.id),
                'inventoryItemId': self.clear_to_str(line_product.id),
                'expectedQuantity': self.clear_to_str(line.product_uom_qty),
                'actualQuantity': self.clear_to_str(line.quantity_done),
                'unitOfMeasureId': self._get_prop(line_product, 'uom_id', 'id'),
                'inventoryItemName': line_product.name,
                'inventoryItemBarcode': self.clear_to_str(line_product.barcode),
                'unitOfMeasureName': self._get_prop(line_product, 'uom_id', 'name'),
                'registrationDate': self.clear_to_str(line_product.create_date),
                'documentId': self.clear_to_str(line.picking_id.id),
                'lastChangeDate': self.clear_to_str(line.write_date),
                'price': self.clear_to_str(line.product_id.lst_price),
                'purchasePrice': self.clear_to_str(line.product_id.standard_price),
                'sourceDocumentId': line.picking_id.origin,
            }))
        return vals

    def convert_table_rows(self, odoo_rows, api_to_odoo_field_map: dict):
        """
        Default plain odoo's rows convertor to result list
        @param odoo_rows: odoo rows
        @param api_to_odoo_field_map: field map
        @return: array of converted rows
        """
        result = []
        for row in odoo_rows:
            api_row = {}
            for (api_name, field_info) in api_to_odoo_field_map.items():
                if field_info.odoo_type:
                    prop_value = self._get_prop(row, field_info.odoo_name)
                    api_row[field_info.api_name] = field_info.api_type(prop_value)
            result.append(api_row)
        return result

    def convert_odoo_location_to_cell(self, odoo_location):
        """
        Converts odoo location object to InventoryAPI cell (location)
        @param odoo_location:
        @return:
        """
        return {
            'id': str(odoo_location.id),
            'name': str(odoo_location.complete_name),
            'barcode': str(odoo_location.complete_name)
        }

    def convert_odoo_lot_to_series(self, odoo_lot):
        """
        Converts odoo lot object to series
        @param odoo_lot:
        @return:
        """
        return self._clear_output_dict({
            'id': str(odoo_lot.id),
            'seriesName': str(odoo_lot.name),
            'barcode': str(odoo_lot.name),
            'seriesDate': str(odoo_lot.create_date),
            'seriesKey': str(odoo_lot.product_id.id)
        })

    def is_non_empty_str_in_dict(self, d, key):
        """
        Routine if dict contains non empty d[key] equal to if d.get(key): expression
        @param d:
        @param key:
        @return:
        """
        return key in d and d[key] and str(d[key]) != ''

    def _get_product_name(self, prod: Product):
        """
        Get name of the product from the product object
        @param prod:
        @return:
        """
        return prod.display_name

    def _clear_output_dict(self, d):
        resd = {}
        for key, value in d.items():
            if value != None and value != '':
                resd[key] = value
        return resd

    def clear_to_str(self, s):
        """
        Safe convert object to string
        @param s:
        @return:
        """
        if s is None or s == False:
            return ''
        else:
            return str(s)

    def _get_prop(self, obj, *props):
        for prop in props:
            if obj is None or not bool(obj):
                return None
            obj = getattr(obj, prop)
        return self.clear_to_str(obj)
