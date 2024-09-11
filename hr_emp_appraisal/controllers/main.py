# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, SUPERUSER_ID, _
from odoo.addons.survey.controllers.main import Survey
from odoo.http import request
from werkzeug import urls


class Survey(Survey):

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='json', auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        res = super(Survey, self).survey_submit(survey_token, answer_token, **post)
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']

        url = '%s?%s' % (survey_sudo.get_print_url(), urls.url_encode({'answer_token': answer_sudo and answer_sudo.access_token or None}))
        try:
            template_id = request.env.ref('hr_emp_appraisal.hr_emp_appraisal_send_review_notification')
        except ValueError:
            template_id = False

        template_id.sudo().with_context({'url': url}).send_mail(survey_sudo.id, force_send=False, raise_exception=False)
        return res