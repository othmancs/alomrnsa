from odoo.api import Environment
from .documents_stock_picking_base import DocumentStockPickingImplBase


class DocumentAllocationImpl(DocumentStockPickingImplBase):
    """
    Overrides to process Allocation documents
    """

    def get_stock_picking_filter(self, env: Environment, document_type_name: str):
        # filter only input source locations
        return [('state', '=', 'assigned'),
                ('picking_type_id.sequence_code', '=', 'INT'),
                ('location_id.name', '=', 'Input')]

    def is_support_document_type_name(self, document_type_name: str) -> bool:
        return document_type_name == 'Allocation'
