from odoo.api import Environment
from .documents_pick_and_ship import DocumentPickAndShipImpl
from .documents_receiving import DocumentReceivingImpl
from .documents_allocation import DocumentAllocationImpl
from .documents_pick import DocumentPickImpl
from .documents_ship import DocumentShipImpl


class DocumentImpl:
    """
    Functions to process /documents endpoints.
    """

    # particular document's processor (selecting by its Inventory API type names)
    _doc_processors = {
        'receiving': DocumentReceivingImpl(),
        'allocation': DocumentAllocationImpl(),
        'pick': DocumentPickImpl(),
        'ship': DocumentShipImpl()
    }

    def get_descriptions(self, env: Environment, document_type_name: str, offset, limit, request_count: bool):
        """
        Returns document's headers page by passed arguments
        @param env: Environment
        @param document_type_name: Inventory API document type name
        @param offset: offset of the requesting page
        @param limit:  maximum number of the records in returning result
        @param request_count: need to return total number of records in filter?
        @return:
        """
        if not document_type_name.lower() in self._doc_processors:
            return {'result': []}
        return self._doc_processors[document_type_name.lower()].get_descriptions(env, document_type_name, offset, limit,
                                                                                 request_count)

    def get_document(self, env: Environment, search_mode: str, search_code: str, document_type_name: str):
        """
        Returns document with expected and actual(optional) lines
        @param env: Environment
        @param search_mode: How to find document
        @param search_code: Identifier using for the search process
        @param document_type_name: the document's type name
        @return:
        """
        if not document_type_name.lower() in self._doc_processors:
            return {'document': None}

        return self._doc_processors[document_type_name.lower()].get_document(env, search_mode, search_code,
                                                                             document_type_name)

    def set_document(self, env: Environment, doc):
        """
        Processes finished document in odoo (modify or add stock.move.lines and validates document)
        @param env: Environment
        @param doc: Inventory API document
        @return:
        """
        document_type_name = doc['documentTypeName']
        if not document_type_name.lower() in self._doc_processors:
            return 200
        return self._doc_processors[document_type_name.lower()].set_document(env, doc)
