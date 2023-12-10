from odoo.api import Environment
from .documents_stock_picking_base import DocumentStockPickingImplBase


class DocumentPickAndShipImpl(DocumentStockPickingImplBase):
    """
    @deprecated Overrides to process PickAndShip documents
    """

    def get_stock_picking_filter(self, env: Environment, document_type_name: str):
        return [('picking_type_id.code', '=', 'outgoing'), ('state', '=', 'assigned')]

    def is_support_document_type_name(self, document_type_name: str) -> bool:
        return document_type_name == 'PickAndShip'
