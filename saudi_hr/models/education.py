# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class EducationCertificate(models.Model):
    _name = 'education.certificate'
    _description = 'Education Certificate'

    name = fields.Char(string='Name', required=True)


class EducationStudy(models.Model):
    _name = 'education.study'
    _description = 'Education Study'

    name = fields.Char(string='Name', required=True)


class EducationSchool(models.Model):
    _name = 'education.school'
    _description = 'Education School'

    name = fields.Char(string='Name', required=True)