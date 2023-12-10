from typing import List
from .field_info import FieldInfo
from .tables_base import TableProcessorBase
from odoo.api import Environment


class TableCellsProcessor(TableProcessorBase):
    """
    Process location (cells) table requests.
    The structure of the TableLocationRow object is:
    id
    warehouseId
    name
    barcode
    description
    """

    _mapping_fields: List[FieldInfo] = [
        FieldInfo(api_name_arg='id', api_type_arg=str, odoo_name_arg='id', odoo_type_arg=int),
        FieldInfo(api_name_arg='name', api_type_arg=str, odoo_name_arg='complete_name', odoo_type_arg=str),
        # fake fields to convert query
        FieldInfo(api_name_arg='warehouseid', api_type_arg=str, odoo_name_arg='warehouseid', odoo_type_arg=str),
        FieldInfo(api_name_arg='barcode', api_type_arg=str, odoo_name_arg='barcode', odoo_type_arg=str)
    ]

    def __init__(self):
        self._api_to_odoo_map = FieldInfo.create_api_to_odoo_field_map(self._mapping_fields)

    def _get_rows_int(self, env: Environment, query, device_info, offset, limit, request_count: bool):
        where_root = query.get('whereTreeRoot')
        result = [None, None]

        pick_doc = self.cutils.get_odoo_doc_from_device_info(env, device_info)

        buisness_query = self._query_converter.convert_api_where_expression_to_domain_filter(where_root,
                                                                                             self._api_to_odoo_map)
        buisness_query = self._remove_warehouse_id_filter(buisness_query)
        buisness_query = self._alternate_barcode_field_as_name(buisness_query)
        domain_query = [('active', '=', True)]
        self.cutils.append_company_filter_by_doc(domain_query, pick_doc)

        location_parent_path = self.cutils.get_location_parent_path_from_document(pick_doc)
        if location_parent_path:
            domain_query.append(('parent_path', '=like', location_parent_path + '%'))
        domain_query.extend(buisness_query)

        if request_count:
            result[0] = len(env['stock.location'].search(domain_query))

        locations = env['stock.location'].search(domain_query, limit=limit, offset=offset, order='id ASC')
        locations = self._filter_only_lowest_locations(env, locations)
        result[1] = [self._model_converter.convert_odoo_location_to_cell(loc) for loc in locations]
        return result

    def _alternate_barcode_field_as_name(self, domain_filter):
        corrected_filter = []
        for i in range(len(domain_filter)):
            filter_element = domain_filter[i]
            if isinstance(filter_element, tuple):
                if filter_element[0] == 'barcode':
                    corrected_filter.extend(['|', filter_element, ('complete_name', '=', filter_element[2])])
                    continue
            corrected_filter.append(filter_element)
        return corrected_filter

    def _remove_warehouse_id_filter(self, domain_filter):
        return self._remove_domain_filter_by_none_id_expr(domain_filter, 'warehouseid')

    def _if_allow_only_lowest_cells(self, env):
        return bool(env['ir.config_parameter'].sudo().get_param('clv_api.clv_allow_only_lowest_level_locations'))

    def _filter_only_lowest_locations(self, env: Environment, locations):
        if not self._if_allow_only_lowest_cells(env):
            return locations
        result = []
        for loc in locations:
            domain_filter = [('complete_name', '=like', loc.complete_name + '/%')]
            if len(env['stock.location'].search(domain_filter, limit=1)) == 0:
                result.append(loc)
        return result
