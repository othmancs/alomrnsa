import datetime
from typing import List

from odoo.release import version_info
from .field_info import FieldInfo
from .tables_base import TableProcessorBase
from odoo.api import Environment


class TableSeriesProcessor(TableProcessorBase):
    """
    Process series (lots) table requests.
    The structure of the TableSeriesRow object is:
    barcode:
    code:
    description:
    id:
    number:
    search:
    seriesDate:
    seriesKey:
    seriesName:
    sortIndex:
    """

    _mapping_fields: List[FieldInfo] = [
        FieldInfo(api_name_arg='id', api_type_arg=str, odoo_name_arg='id', odoo_type_arg=int),
        FieldInfo(api_name_arg='seriesName'.lower(), api_type_arg=str, odoo_name_arg='name', odoo_type_arg=str),
        FieldInfo(api_name_arg='seriesDate'.lower(), api_type_arg=str, odoo_name_arg='create_date',
                  odoo_type_arg=datetime.datetime),
        # fake fields to allow convert query
        FieldInfo(api_name_arg='seriesKey'.lower(), api_type_arg=str, odoo_name_arg='seriesKey', odoo_type_arg=str),
        FieldInfo(api_name_arg='barcode', api_type_arg=str, odoo_name_arg='barcode', odoo_type_arg=str),
        FieldInfo(api_name_arg='seriesKey'.lower(), api_type_arg=str, odoo_name_arg='product_id', odoo_type_arg=int)
    ]

    def __init__(self):
        self._api_to_odoo_map = FieldInfo.create_api_to_odoo_field_map(self._mapping_fields)

    def _get_rows_int(self, env: Environment, query, device_info, offset, limit, request_count: bool):
        where_root = query.get('whereTreeRoot')
        result = [None, None]

        buisness_query = self._query_converter.convert_api_where_expression_to_domain_filter(where_root,
                                                                                             self._api_to_odoo_map)
        buisness_query = self._remove_series_key_filter(buisness_query)
        buisness_query = self._alternate_barcode_field_as_name(buisness_query)
        domain_query = [('product_id.product_tmpl_id.tracking', '=', 'lot')]
        pick_doc = self.cutils.get_odoo_doc_from_device_info(env, device_info)
        self.cutils.append_company_filter_by_doc(domain_query, pick_doc)
        domain_query.extend(buisness_query)

        stock_lot_entity_name = self.cutils.get_stock_lot_env_name()
        if request_count:
            result[0] = len(env[stock_lot_entity_name].search(domain_query))

        series = env[stock_lot_entity_name].search(domain_query, limit=limit, offset=offset, order='id ASC')
        result[1] = [self._model_converter.convert_odoo_lot_to_series(elem) for elem in series]
        return result

    def _alternate_barcode_field_as_name(self, domain_filter):
        corrected_filter = []
        for i in range(len(domain_filter)):
            filter_element = domain_filter[i]
            if isinstance(filter_element, tuple):
                if filter_element[0] == 'barcode':
                    corrected_filter.extend(['|', filter_element, ('name', '=', filter_element[2])])
                    continue
            corrected_filter.append(filter_element)
        return corrected_filter

    def _remove_series_key_filter(self, domain_filter):
        return self._remove_domain_filter_by_none_id_expr(domain_filter, 'serieskey')
