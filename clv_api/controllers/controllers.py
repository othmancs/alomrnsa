# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response
from odoo.tools import date_utils
from urllib import parse

from .controller_helper_v13 import ControllerHelperV13
from .controller_helper_v14 import ControllerHelperV14
from .controller_helper_v15 import ControllerHelperV15
from .controller_helper_v16 import ControllerHelperV16
from .inventory import InventoryImpl
from .documents import DocumentImpl
from .tables import TablesImpl
from odoo.release import version_info


class ClvApi(http.Controller):
    """
    Entry point of the Inventory API controller (module).
    It supports Inventory API endpoints
    """

    # implementation of the /inventory endpoints
    _inventory_impl = InventoryImpl()
    # implementation of the /documents endpoints
    _documents_impl = DocumentImpl()
    # implementation of the /tables endpoints
    _tables_impl = TablesImpl()

    # controller's helpers to validate input and output objects/dictionaries
    _controller_helpers = {
        13: ControllerHelperV13(),
        14: ControllerHelperV14(),
        15: ControllerHelperV15(),
        16: ControllerHelperV16()
    }

    def __init__(self):
        """
        Ctor
        """
        major_version_code = version_info[0]
        if not major_version_code in self._controller_helpers:
            RuntimeError('Cleverence Inventory API does not support {} version of odoo.'.format(major_version_code))
        self._controller_helper = self._controller_helpers[major_version_code]

    @http.route('/Auth', type='json', auth="public", methods=['POST'])
    def auth(self, **kw):
        """
        @deprecated
        May be used by alternative authorization call.
        @param kw:
        @return:
        """
        params = self._controller_helper.preprocess_request(request)
        request.session.authenticate(params.get('db'),
                                     params.get('login'),
                                     params.get('password'))
        return '{"authResult": "success"}'

    @http.route('/Inventory/getItems', type='json', auth="user", methods=['POST'])
    def inventory_get_items(self, **kw):
        """
        /Inventory/getItems endpoint implementation. Used to get page of inventory items.
        @param kw:
        @return: Dictionary as described in Inventory API swagger model
        """
        params = self._controller_helper.preprocess_request(request)
        return self._inventory_impl.get_items(http.request.env,
                                              params.get('parentId'),
                                              params.get('offset'),
                                              params.get('limit'),
                                              params.get('requestCount'))

    @http.route('/Inventory/getItemsByString', type='json', auth="user", methods=['POST'])
    def inventory_get_items_by_string(self, **kw):
        """
        '/Inventory/getItemsByString' endpoint implementation. Used to search inventory items by string match.
        @param kw:
        @return: Dictionary as described in Inventory API swagger model
        """
        params = self._controller_helper.preprocess_request(request)
        return self._inventory_impl.get_items_by_string(http.request.env,
                                                        params.get('matchString'),
                                                        params.get('offset'),
                                                        params.get('limit'),
                                                        params.get('requestCount'))

    @http.route('/Inventory/getItemsByIds', type='json', auth="user", methods=['POST'])
    def inventory_get_items_by_ids(self, **kw):
        """
        '/Inventory/getItemsByIds' endpoint implementation. Used to get inventory items with specified UOM ids.
        @param kw:
        @return: Dictionary as described in Inventory API swagger model
        """
        params = self._controller_helper.preprocess_request(request)
        return self._inventory_impl.get_items_by_ids(http.request.env, params.get('idList'))

    @http.route('/Inventory/getItemsBySearchCode', type='json', auth="user", methods=['POST'])
    def inventory_get_items_by_search_code(self, **kw):
        """
        '/Inventory/getItemsBySearchCode' implementation. Used to search inventory Item by id, marking or barcode.
        @param kw:
        @return: Dictionary as described in Inventory API swagger model
        """
        params = self._controller_helper.preprocess_request(request)
        return self._inventory_impl.get_items_be_search_code(http.request.env,
                                                             params.get('searchMode'),
                                                             params.get('searchData'))

    @http.route('/Documents/getDocumentDescriptions', auth='user', type='json', methods=['POST'])
    def get_documents_desc(self, **kw):
        """
        '/Documents/getDocumentDescriptions' endpoint implementation. Used to get list of document's headers
        @param kw:
        @return: Dictionary as described in Inventory API swagger model
        """
        params = self._controller_helper.preprocess_request(request)
        return self._documents_impl.get_descriptions(http.request.env,
                                                     params.get('documentTypeName'),
                                                     params.get('offset'),
                                                     params.get('limit'),
                                                     params.get('requestCount'))

    @http.route('/Documents/getDocument', auth='user', type='json', methods=['POST'])
    def get_document(self, **kw):
        """
        '/Documents/getDocument' endpoint implementation. Used to get full document (with expected and actual lines).
        @param kw:
        @return: Dictionary as described in Inventory API swagger model
        """
        params = self._controller_helper.preprocess_request(request)
        return self._documents_impl.get_document(http.request.env,
                                                 params.get('searchMode'),
                                                 params.get('searchCode'),
                                                 params.get('documentTypeName'))

    @http.route('/Documents/setDocument', auth='user', type='json', methods=['POST'])
    def set_document(self, **kw):
        """
        '/Documents/setDocument' endpoint implementation. Used to process finished document in odoo.
        @param kw:
        """
        params = self._controller_helper.preprocess_request(request)
        return self._documents_impl.set_document(http.request.env, params.get('document'))

    @http.route('/Tables/getTable', auth='user', type='json', methods=['POST'])
    def tables_get_items(self, **kw):
        """
        '/Tables/getTable' endpoint implementation. Used to get table's rows page by query.
        @param kw:
        @return: Dictionary as described in Inventory API swagger model
        """
        params = self._controller_helper.preprocess_request(request)
        return self._tables_impl.get_rows(http.request.env,
                                          params.get('query'),
                                          params.get('deviceInfo'),
                                          params.get('offset'),
                                          params.get('limit'),
                                          params.get('requestCount'))
