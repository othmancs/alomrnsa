from odoo import fields, models, _, modules
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
# import arabic_reshaper
# from bidi.algorithm import get_display
from odoo.http import request
from . import amount_to_text_ar 



class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_print_check(self):
        font_size = self.journal_id.font_size
        if font_size == 0 : font_size = 30
        
        tff_path = modules.module.get_resource_path(
            'check_print_arabic',
            'static/src',
            'NeoSansArabicBold.ttf'
        )
        font = ImageFont.truetype(tff_path, size = font_size)

        partner = self.partner_id.name
        if not partner:
            partner = "Test Check Partner"
        partner_width, partner_height = font.getsize(partner)

        ref = self.ref 
        if not ref:
            ref="Test Check Describtion"
        ref_width, ref_height = font.getsize(ref)

        image = Image.new('RGB', size=(3508, 2480) , color = (255,255,255))
        draw = ImageDraw.Draw(image)
        
        # format text to display
        
        amount_text = amount_to_text_ar.amount_to_text(self.amount)
        
        amount_text_width, amount_text_height = font.getsize(amount_text)
        
       

        dt = fields.Date.from_string(self.date).strftime('%Y-%m-%d')
        draw.text((self.journal_id.date_h ,                              self.journal_id.date_v         ), text=dt, font=font, fill="#000000")
        draw.text((self.journal_id.partner_h - partner_width,            self.journal_id.partner_v      ), text=partner, font=font, fill="#000000")
        print('----------------1')
        draw.text((self.journal_id.amount_words_h - amount_text_width ,  self.journal_id.amount_words_v ), text=amount_text, font=font, fill="#000000")
        print('----------------2')
        draw.text((self.journal_id.place_h,                              self.journal_id.place_v        ), text=self.journal_id.place, font=font, fill="#000000")
        draw.text((self.journal_id.notes_h- ref_width,                   self.journal_id.notes_v        ), text=ref, font=font, fill="#000000")
        draw.text((self.journal_id.amount_h,                             self.journal_id.amount_v       ), text='#'+f"{self.amount:,}"+'#', font=font, fill="#000000")
        print('----------------',amount_text)
        buffered = BytesIO()
        image.save(buffered, format="png")
        
        base64_image = base64.b64encode(buffered.getvalue())

        file_name = str(self.env.uid)+"_bank_check.png"
        attachment_id = self.env['ir.attachment'].search([('name', '=', file_name)], limit=1)
        if attachment_id:
            attachment_id.unlink()
        attachment_id = self.env['ir.attachment'].create(
            {
                'name': file_name,
                'datas': base64_image,
            }) 
        url = 'https://' + request.httprequest.__dict__['environ']['HTTP_HOST'] + '/web/content/?model=ir.attachment&id=%s&filename_field=datas_fname&field=datas&download=true' % (attachment_id.id)
		
        return {
				'type': "ir.actions.act_url",
				'url': url,
				'target': "new"
			}
    
    