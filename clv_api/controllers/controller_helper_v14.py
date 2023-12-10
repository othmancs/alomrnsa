from .controller_helper_base import ControllerHelperBase, prepare_response_to_plain_json


class ControllerHelperV14(ControllerHelperBase):
    """
    Implements controller helper for odoo v14
    """

    def _ensure_plain_response(self, request):
        request._json_response = prepare_response_to_plain_json.__get__(request, type(request))

    def _get_json_request(self, request):
        return request.jsonrequest