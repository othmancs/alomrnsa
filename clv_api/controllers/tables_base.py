from abc import abstractmethod
from typing import List
from odoo.api import Environment
from .model_converter import ModelConverter
from .query_converter import QueryConverter
from .common_utils import CommonUtils

class TableProcessorBase:
    """
    Base table request processor
    """
    _model_converter = ModelConverter()
    _query_converter = QueryConverter()
    cutils = CommonUtils()

    def get_rows(self, env: Environment, query, device_info, offset, limit, request_count: bool):
        """
        Returns the page of rows depends on passed query
        @param env: Environment
        @param query: Inventory API query object
        @param device_info: Inventory API DeviceInfo
        @param offset: first record index to return
        @param limit: the maximum number of records to return
        @param request_count: need to return total number of records in query
        @return:
        """
        res_list = self._get_rows_int(env, query, device_info, offset, limit, request_count)
        result = {}
        if res_list[0]:
            result['totalCount'] = res_list[0]
        result['result'] = res_list[1]
        return result

    @abstractmethod
    def _get_rows_int(self, env: Environment, query, device_info, offset, limit, request_count: bool) -> List:
        """
        Returns the page of rows depends on passed query
        @param env: Environment
        @param query: Inventory API query object
        @param device_info: Inventory API DeviceInfo
        @param offset: first record index to return
        @param limit: the maximum number of records to return
        @param request_count: need to return total number of records in query
        @return:
        """
        pass

    def _remove_domain_filter_by_none_id_expr(self, domain_filter, field_name):
        """
        Removes domain filter by replacing it by id != none
        """
        corrected_filter = []
        for i in range(len(domain_filter)):
            filter_element = domain_filter[i]
            if isinstance(filter_element, tuple):
                if filter_element[0].lower() == field_name.lower():
                    # to be sure this filter is always true (id is always non-empty)
                    filter_element = ('id', '!=', False)
            corrected_filter.append(filter_element)
        return corrected_filter

