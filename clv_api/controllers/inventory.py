from odoo.api import Environment
from odoo.release import version_info
from .model_converter import ModelConverter


class InventoryImpl:
    """
    Supports implementation of the /inventory endpoint functions of the Inventory API
    """
    _model_converter = ModelConverter()

    def get_items(self, env: Environment, parent_id: str, offset, limit, request_count: bool):
        """
        Returns the page of the inventory items (products)
        @param env: Environment
        @param parent_id: parent id for the category or None
        @param offset: the first record index to be returned
        @param limit: the maximum number of records
        @param request_count: Need to return total number of records
        @return:
        """
        result_list = []
        template_id_for_folder = self._model_converter.get_template_id_from_folder_id(parent_id)
        if not limit:
            limit = 100
        if template_id_for_folder != '':
            templates = env['product.template'].search([('id', 'in', [int(template_id_for_folder)])])
            if not templates or len(templates) != 1:
                raise Exception('No such folder with id ' + template_id_for_folder + ' found')
            template = templates[0]
            for prod in template.product_variant_ids:
                result_list.append(self._make_inventory_item_result(
                    self._model_converter.product_to_inventory_item(env, prod),
                    self._model_converter.product_to_related_data(env, prod)))
        else:
            product_templates = env['product.template'].search([(self._get_detailed_type_name(), '=', 'product'), ('active', '=', True)],
                                                               limit=limit, offset=offset)
            for product_template in product_templates:
                result_list.append(self._make_inventory_item_result(
                    self._model_converter.product_template_to_inventory_item(env, product_template),
                    self._model_converter.product_template_to_related_data(env, product_template)))
        return {"result": result_list}

    def get_items_by_string(self, env: Environment, match_str: str, offset, limit, request_count: bool):
        """
        Searches products by string match
        @param env: Environment
        @param match_str: string to search by
        @param offset: the first record index to be returned
        @param limit: the maximum number of records
        @param request_count: Need to return total number of records
        @return:
        """
        product_template_ids = env['product.template'].search(
                [('name', 'ilike', match_str), ('active', '=', True)], limit=limit, offset=offset, order='id ASC')
        result_data_list = []
        for pt_id in product_template_ids:
            result_data_list.append(self._make_inventory_item_result(
                self._model_converter.product_template_to_inventory_item(env, pt_id),
                self._model_converter.product_template_to_related_data(env, pt_id)
            ))
        return {"result": result_data_list}

    def get_items_by_ids(self, env: Environment, ids_list : list):
        """
        Searches products, and it's unit of measures
        @param env: Environment
        @param ids_list: requested pairs of product's ids and uom ids
        @return:
        """
        item_ids = [id_elem['inventoryItemId'] for id_elem in ids_list]

        products = env['product.product'].search([('id', 'in', item_ids)])
        result_data_list = []
        for prod in products:
            result_data_list.append(self._make_inventory_item_result(
                self._model_converter.product_to_inventory_item(env, prod),
                self._model_converter.product_to_related_data(env, prod)
            ))
        return {"result": result_data_list}

    def get_items_be_search_code(self, env: Environment, search_mode, search_data):
        """
        Searches products by id' marking or barcode
        @param env: Environment
        @param search_mode: how to search (by what field or entity)
        @param search_data: data used by search process
        @return:
        """
        if not search_mode:
            search_mode = {'byId': 'True'}

        search_list = []

        if 'byId' in search_mode and bool(search_mode['byId']):
            if self._model_converter.is_non_empty_str_in_dict(search_data, 'raw'):
                if self._model_converter.is_product_id_folder(search_data['raw']):
                    raw_id = self._model_converter.get_template_id_from_folder_id(search_data['raw'])
                    product_tmpls = env['product.template'].search([('id', 'in', [raw_id])])
                    return {"result": self._make_inventory_item_result_list_from_templates(env, product_tmpls)}
                else:
                    raw_id = search_data['raw']
                    search_list.append(('id', 'in', [raw_id]))
        if 'byBarcode' in search_mode and bool(search_mode['byBarcode']):
            if self._model_converter.is_non_empty_str_in_dict(search_data, 'ean13'):
                search_list.append(('barcode', '=', search_data['ean13']))
            if self._model_converter.is_non_empty_str_in_dict(search_data, 'gtin14'):
                search_list.append(('barcode', '=', search_data['gtin14']))
            if self._model_converter.is_non_empty_str_in_dict(search_data, 'ean8'):
                search_list.append(('barcode', '=', search_data['ean8']))
            if self._model_converter.is_non_empty_str_in_dict(search_data, 'upca'):
                search_list.append(('barcode', '=', search_data['upca']))
            if self._model_converter.is_non_empty_str_in_dict(search_data, 'upce'):
                search_list.append(('barcode', '=', search_data['upce']))
            if self._model_converter.is_non_empty_str_in_dict(search_data, 'raw'):
                search_list.append(('barcode', '=', search_data['raw']))

        if len(search_list) > 1:
            new_search_list = []
            for i in range(0, len(search_list) - 1):
                new_search_list.append('|')
            new_search_list.extend(search_list)
            search_list = new_search_list

        search_list.append(('active', '=', True))

        products = env['product.product'].search(search_list)
        return {"result": self._make_inventory_item_result_list(env, products)}

    def _make_inventory_item_result(self, inventory_item, related_data):
        return {
                'inventoryItem': inventory_item,
                'relatedData': related_data
            }

    def _make_inventory_item_result_list(self, env : Environment, products):
        result_data_list = []
        for prod in products:
            result_data_list.append(self._make_inventory_item_result(
                self._model_converter.product_to_inventory_item(env, prod),
                self._model_converter.product_to_related_data(env, prod)
            ))
        return result_data_list

    def _make_inventory_item_result_list_from_templates(self, env : Environment, product_templates):
        result_data_list = []
        for prod_template in product_templates:
            result_data_list.append(self._make_inventory_item_result(
                self._model_converter.product_template_to_inventory_item(env, prod_template),
                self._model_converter.product_template_to_related_data(env, prod_template)
            ))
        return result_data_list

    def _get_detailed_type_name(self):
        if version_info[0] <= 14:
            return 'type'
        else:
            return 'detailed_type'


