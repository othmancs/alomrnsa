# -*- coding: utf-8 -*-
##############################################################################
#    Copyright (C) 2020 AtharvERP (<http://atharverp.com/>). All Rights Reserved
# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, atharverp.com or you have written agreement from
# author of this software owner.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
##############################################################################

from odoo import models


class ProductTempExt(models.Model):

    _inherit = 'product.template'

    def clear_duplicates(self):
        unique_product = []  # list of set
        duplicate_products = []
        is_first = True
        for product in self:
            temp_unique_partners = unique_product.copy()
            if not unique_product:
                unique_product.append((product.id, product.default_code))
            if not is_first:
                for uni_pro in temp_unique_partners:
                    if product.default_code == uni_pro[1]:
                        duplicate_products.append(product.id)
                    else:
                        unique_product.append((product.id, product.default_code))
            is_first = False
        self.browse(list(dict.fromkeys(duplicate_products))).unlink()
