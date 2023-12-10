import json
from urllib import parse
from odoo.http import Response
from odoo.tools import date_utils


def extract_pretty_error_test(error):
    """
    Extract pretty-printed error from error object
    @param error: Error object (dictionary)
    @return:
    """
    result = ''
    if 'message' in error:
        result = result + error['message']
    if 'data' in error and 'message' in error['data']:
        result = result + '. ' + error['data']['message']
    if len(result) == 0:
        result = 'ODOO server error. check odoo.log file for details.'
    return result


def prepare_response_to_plain_json(self, result=None, error=None):
    """
    Removes json-rpc headers
    @param self: self object
    @param result: returning result object
    @param error: error object
    @return:
    """
    default_http_code = 200
    response = {}
    if error is not None:
        response = extract_pretty_error_test(error)
        default_http_code = 500
    if result is not None:
        response = result
    mime = 'application/json'
    body = json.dumps(response, default=date_utils.json_default)
    return Response(
        body, status=error and error.pop('http_status', default_http_code) or default_http_code,
        headers=[('Content-Type', mime), ('Content-Length', len(body))]
    )


class ControllerHelperBase:
    """
    Base class of controller's functions processors
    """

    def preprocess_request(self, request):
        """
        Returns dictionary with both body and query params in single dictionary
        @param request:
        @return:
        """
        self._ensure_plain_response(request)
        json_dict = self._get_json_request(request)
        query_dict = dict(parse.parse_qsl(parse.urlsplit(request.httprequest.url).query))
        return {**json_dict, **query_dict}

    def _ensure_plain_response(self, request):
        """
        Ensures that response is plain
        @param request:
        """
        pass


    def _get_json_request(self, request):
        """
        Returns Json (body) part of the query
        @param request:
        """
        pass
