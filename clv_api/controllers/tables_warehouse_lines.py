from typing import List
from odoo.api import Environment
from .field_info import FieldInfo
from .tables_base import TableProcessorBase


class TableWarehouseLinesProcessor(TableProcessorBase):
    """
    Process warehouseLines table requests.
    The structure of the Inventory API table:
    addressable:
        type: boolean
    barcode:
        type: string
    code:
        type: string
    id:
        type: string
    isFolder:
        type: boolean
    name:
        type: string
    parentId:
        type: string
    search:
        type: string
        description: "Concatenated data in a lower case for searching."
    """

    _mapping_fields: List[FieldInfo] = [
        FieldInfo(api_name_arg='id', api_type_arg=str, odoo_name_arg='id', odoo_type_arg=int),
        FieldInfo(api_name_arg='name', api_type_arg=str, odoo_name_arg='name', odoo_type_arg=str),

        #fake for conversion
        FieldInfo(api_name_arg='parentid', api_type_arg=str, odoo_name_arg='parentid', odoo_type_arg=None),
    ]

    def __init__(self):
        self._api_to_odoo_map = FieldInfo.create_api_to_odoo_field_map(self._mapping_fields)

    def _get_rows_int(self, env: Environment, query, device_info, offset, limit, request_count: bool):
        where_root = query.get('whereTreeRoot')
        result = [None, []]
        domain_filter = [('active', '=', True)]

        pick_doc = self.cutils.get_odoo_doc_from_device_info(env, device_info)
        self.cutils.append_company_filter_by_doc(domain_filter, pick_doc)

        if where_root:
            domain_query_list = self._query_converter\
                .convert_api_where_expression_to_domain_filter(where_root, self._api_to_odoo_map)
            if self._is_domain_filter_contains_parent_id(domain_query_list):
                return result
            domain_query_list = self._remove_parent_id_filter(domain_query_list)
            domain_filter.extend(domain_query_list)

        if request_count:
            result[0] = len(env['stock.warehouse'].search(domain_filter))
        result[1] = env['stock.warehouse'].search(domain_filter, limit=limit, offset=offset, order='id ASC')

        converted_list = []
        for elem in result[1]:
            converted_elem = self._model_converter.convert_table_rows(elem, self._api_to_odoo_map)[0]
            self._append_fields_to_result_object(converted_elem)
            converted_list.append(converted_elem)
        result[1] = converted_list
        return result

    def _append_fields_to_result_object(self, result_object):
        result_object['addressable'] = True

    def _remove_parent_id_filter(self, domain_filter):
        return self._remove_domain_filter_by_none_id_expr(domain_filter, 'parentid')

    def _is_domain_filter_contains_parent_id(self, domain_filter):
        for i in range(len(domain_filter)):
            filter_element = domain_filter[i]
            if isinstance(filter_element, tuple):
                if filter_element[0].lower() == 'parentid':
                    return True
        return False
