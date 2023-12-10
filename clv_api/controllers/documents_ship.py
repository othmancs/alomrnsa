from odoo.api import Environment
from .documents_stock_picking_base import DocumentStockPickingImplBase

class DocumentShipImpl(DocumentStockPickingImplBase):

    def get_stock_picking_filter(self, env: Environment, document_type_name: str):
        return [('state', '=', 'assigned'),
                ('picking_type_id.sequence_code', '=', 'OUT')]

    def is_support_document_type_name(self, document_type_name: str) -> bool:
        return document_type_name == 'Ship'