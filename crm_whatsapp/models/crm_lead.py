from odoo import fields,api,models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
	_inherit = 'crm.lead'

	contact_person = fields.One2many("crm.lead.contact","crm_id", string="Contact Person")

class CrmLeadContact(models.Model):
	_name = 'crm.lead.contact'

	name = fields.Char("name")
	country_id = fields.Many2one("res.country", "Select Country")
	phone = fields.Char("Contact Number")
	crm_id = fields.Many2one("crm.lead","Crm Lead ID")

	def open_whatsapp_web(self):
		if self.phone:
			return {
				"type": 'ir.actions.act_url',
				"url": 'https://web.whatsapp.com/send/?phone=+%s%s' % (self.country_id.phone_code,self.phone),
				"target": 'new'
			}
		else:
			raise ValidationError("Please Provide Contact number for %s" % self.name)


	def open_whatsapp_moile(self):
		if self.phone:
			return {
				"type": 'ir.actions.act_url',
				"url": 'https://api.whatsapp.com/send/?phone=+%s%s' % (self.country_id.phone_code,self.phone),
				"target": 'new'
			}
		else:
			raise ValidationError("Please Provide Contact number for %s" % self.name)
