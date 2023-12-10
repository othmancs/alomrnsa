from odoo.api import Environment
from .model_converter import ModelConverter
from .tables_cells import TableCellsProcessor
from .tables_series import TableSeriesProcessor
from .tables_warehouse_lines import TableWarehouseLinesProcessor


class TablesImpl:
    """
    Supports /tables endpoint of the Inventory API
    """
    _model_converter = ModelConverter()

    # particular table rows request processors depends on its names
    _table_processor = {
        'warehouseslines': TableWarehouseLinesProcessor(),
        'locations': TableCellsProcessor(),
        'series': TableSeriesProcessor(),
    }

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
        key = query['from'].lower()
        if key in self._table_processor:
            return self._table_processor[key].get_rows(env, query, device_info, offset, limit, request_count)
        else:
            return {"result": []}