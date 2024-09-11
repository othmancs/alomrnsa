# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Employee(models.Model):
    _name = "emp.health.info"
    _description = "Employee Health Details"

    check_update = fields.Datetime(string="Check update", required=True, default=fields.Datetime.now())
    height = fields.Float(string="Height(feet)", required=True)
    weight = fields.Float(string="Weight(kg)", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    blood_pressure = fields.Integer(string="Blood Pressure")
    cholesterol = fields.Char(string="Cholesterol")
    physically_inactive = fields.Boolean(string='Physically Inactive')
    is_smoking = fields.Boolean(string="Smoking")
    is_alcohol = fields.Boolean(string="Alcohol")
    smoking_type = fields.Selection([('regular', 'Regular'), ('occasionally', 'Occasionally')])
    alcohol_type = fields.Selection([('regular', 'Regular'), ('occasionally', 'Occasionally')])
    bmi_calculation = fields.Selection([('over_weight', 'Over Weight'),
                                        ('under_weight', 'Under Weight'),
                                        ('normal_weight', 'Normal Weight')], required=False, string="BMI Calculation")
    blood_group = fields.Selection([('a+', 'A+'),
                                    ('a-', 'A-'),
                                    ('b+', 'B+'),
                                    ('b-', 'B-'),
                                    ('o+', 'O+'),
                                    ('o-', 'O-'),
                                    ('ab+', 'AB+'),
                                    ('ab-', 'AB-')], required=True, string="Blood Group")
    stress_level = fields.Selection([('high_stress', 'High Stress'),
                                     ('distress', 'Distress')], string="Stress Level")

    @api.onchange('height', 'weight')
    def onchange_bmi_calculation(self):
        """
            calculate the BMI based on height and weight
        """
        for rec in self:
            if rec.height and rec.weight:
                meter = 0.3048
                height_meter = rec.height * meter
                bmi_result = rec.weight / (height_meter * height_meter)
                if bmi_result < 18.5:
                    rec.bmi_calculation = 'under_weight'
                elif bmi_result >= 18.5 and bmi_result < 24.9:
                    rec.bmi_calculation = 'normal_weight'
                elif bmi_result >= 24.9:
                    rec.bmi_calculation = 'over_weight'
