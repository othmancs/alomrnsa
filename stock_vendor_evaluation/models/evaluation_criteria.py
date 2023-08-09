from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)


class EvaluationCriteria(models.Model):
    _name = 'evaluation.criteria'
    _description = 'Evaluation Criteria'

    sequence = fields.Integer()
    name = fields.Char()
    description = fields.Char()
    value = fields.Float(required=True)

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, _('%s (%s)') % (rec.name, rec.value)))
        return res