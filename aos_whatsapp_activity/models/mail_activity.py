# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

from collections import namedtuple
import html2text
from odoo.addons.aos_whatsapp.klikapi import texttohtml

from datetime import datetime, date, timedelta, time

class MailActivity(models.Model):
    _inherit = 'mail.activity'
    #_inherit = ['mail.activity', 'portal.mixin', 'mail.thread', 'mail.activity.mixin']
    
    date_schedule = fields.Datetime('Schedule Reminder', index=True, required=True, default=fields.Datetime.now)
    activity_whatsapp_notif = fields.Boolean('Notification (Whatsapp)')
    activity_whatsapp_counter = fields.Integer('Counter (Whatsapp)', default=1)
    
    def get_link(self):
        for ts in self:
            base_url = ts.get_base_url()
            share_url = ts._get_share_url(redirect=True, signup_partner=True)
            url = base_url + share_url
            return url
        
    # def _get_number_of_days(self, date_from, date_to, employee_id):
    #     """ Returns a float equals to the timedelta between two dates given as string."""
    #     if employee_id:
    #         employee = self.env['hr.employee'].browse(employee_id)
    #         return employee._get_work_days_data_batch(date_from, date_to)[employee.id]
    #
    #     today_hours = self.env.company.resource_calendar_id.get_work_hours_count(
    #         datetime.combine(date_from.date(), time.min),
    #         datetime.combine(date_from.date(), time.max),
    #         False)
    #
    #     hours = self.env.company.resource_calendar_id.get_work_hours_count(date_from, date_to)
    #     return {'days': hours / (today_hours or HOURS_PER_DAY), 'hours': hours}
    
    def _prepare_mail_message(self, author_id, chat_id, record, model, body, data, subject, partner_ids, attachment_ids, response, status):
        values = {
            'author_id': author_id,
            'model': model or 'res.partner',
            'res_id': record,
            'body': body,
            'whatsapp_data': data,
            'subject': subject or False,
            'message_type': 'whatsapp',
            'record_name': subject,
            'partner_ids': [(4, pid) for pid in partner_ids],
            'attachment_ids': attachment_ids and [(6, 0, attachment_ids.ids)],
            'whatsapp_method': data['method'],
            'whatsapp_chat_id': chat_id,
            'whatsapp_response': response,
            'whatsapp_status': status,
        }
        #print ('===_prepare_mail_message===',values)
        return values
    
    def _send_whatsapp_activity(self, activity_whatsapp_counter=None):
        #calendar = self._get_calendar()
        today = fields.Date.today()
        today_time = fields.Datetime.now()
        MailMessage = self.env['mail.message']
        activity_employees = self.env['mail.activity'].search([('activity_whatsapp_notif','=',True),('date_schedule','<=',today_time)])
        #print ('====kirim====',activity_employees)
        for activity in activity_employees.filtered(lambda a: a.user_id.partner_id.whatsapp and a.user_id.partner_id.country_id):
            #RESET EMAIL KE 3    
            #print ('==employee==',employee)
            # employee_tz = employee.tz or 'UTC'
            # user_tz = timezone(employee.tz if employee.tz else 'UTC')
            #
            # resource_calendar_id = employee.resource_calendar_id or self.env.company.resource_calendar_id
            # domain = [('calendar_id', '=', resource_calendar_id.id), ('display_type', '=', False)]
            # attendances = self.env['resource.calendar.attendance'].read_group(domain, ['ids:array_agg(id)', 'hour_from:min(hour_from)', 'hour_to:max(hour_to)', 'week_type', 'dayofweek', 'day_period'], ['week_type', 'dayofweek', 'day_period'], lazy=False)
            #
            # # Must be sorted by dayofweek ASC and day_period DESC
            # attendances = sorted([DummyAttendance(group['hour_from'], group['hour_to'], group['dayofweek'], group['day_period'], group['week_type']) for group in attendances], key=lambda att: (att.dayofweek, att.day_period != 'morning'))
            #
            # default_value = DummyAttendance(0, 0, 0, 'morning', False)
            #
            # #tz = self.env.user.tz if self.env.user.tz and not self.request_unit_custom else 'UTC'  # custom -> already in UTC
            # attendance_from = next((att for att in attendances if int(att.dayofweek) >= today.weekday()), attendances[0] if attendances else default_value)
            # attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= today.weekday()), attendances[-1] if attendances else default_value)
            #
            # hour_from = float_to_time(attendance_from.hour_from - 1.0) #MUNDUR 1 JAM
            # hour_to = float_to_time(attendance_to.hour_to)
            #
            # #print ('===activity_employees=22=',attendance_from,attendance_to)
            # date_from = timezone(employee_tz).localize(datetime.combine(today, hour_from)).astimezone(user_tz).replace(tzinfo=None)
            # date_to = timezone(employee_tz).localize(datetime.combine(today, hour_to)).astimezone(user_tz).replace(tzinfo=None)
            #
            # number_of_days = 0
            # #print ('===activity_employees=11=',user_tz,today_timezone,global_from,activity_employees,today,today_time,number_of_days)
            # if date_from and date_to:
            #     #number_of_days = employee._get_work_days_data_batch(date_from, date_to)[employee.id]['days']
            #     number_of_days = self._get_number_of_days(date_from, date_to, employee.id)['days']
            #print ('===activity_employees=22=',self.env['account.analytic.line'].search([('date','=',today),('employee_id','=',employee.id)]))
            #print ('==employee==',employee.name,employee_tz,user_tz,date_from,date_to,today,number_of_days) 
            # if employee.activity_whatsapp_counter == activity_whatsapp_counter\
            #     and not self.env['account.analytic.line'].search([('date','=',today),('employee_id','=',employee.id)]):
                #template_id = self.env.ref('aos_hr_activity.email_template_activity_reminder_1', raise_if_not_found=False)
                #print ('====',employee.name,employee.activity_whatsapp_counter,activity_whatsapp_counter)
            if activity_whatsapp_counter == 1 and activity.activity_whatsapp_counter == activity_whatsapp_counter:#18.00
                template_id = self.env.ref('aos_whatsapp_activity.email_template_whatsapp_notification', raise_if_not_found=False)
                #activity_users += activity.employee_id.email
            elif activity_whatsapp_counter == 2 and  activity.activity_whatsapp_counter == activity_whatsapp_counter:#20.00
                template_id = self.env.ref('aos_whatsapp_activity.email_template_whatsapp_notification', raise_if_not_found=False)
                #activity_users += activity.employee_id.email
            elif activity_whatsapp_counter == 3 and  activity.activity_whatsapp_counter == activity_whatsapp_counter:#22.00
                template_id = self.env.ref('aos_whatsapp_activity.email_template_whatsapp_notification', raise_if_not_found=False)
                #activity_users += activity.employee_id.email
            #activity_users += activity.employee_id.email
            #print ('===BELUM ISI TIMESHEET==',template_id,activity_whatsapp_counter,activity.activity_whatsapp_counter)
            try:
                template = template_id.generate_email(activity.id)
                body = template.get('body')
                subject = template.get('subject')
                #print ('==link==',self.env.user.company_id.website_url,str(activity.id))#+"/mail/view?model=mail.activity&amp;res_id=%s" % (str(activity.id)))
                message = body# + self.env.user.company_id.website_url+"/mail/view?model=mail.activity&amp;res_id=%s" % (str(activity.id))
                #MESSAGE SENT
                if message:
                    send_message = {}
                    status = 'pending'
                    #for tapp in activity_approver_users:
                    whatsapp = activity.user_id.partner_id._formatting_mobile_number()
                    message_data = {
                        'method': 'sendMessage',
                        'phone': whatsapp,
                        'body': html2text.html2text(message),
                        'origin': subject,
                        'link': '',
                    }
                    #print ('==message_data=',self.env.user.partner_id.id, None, activity and activity.id, 'mail.activity', message, message_data, activity.summary, [activity.id], [], send_message, status)
                    vals = self._prepare_mail_message(self.env.user.partner_id.id, None, activity and activity.id, 'mail.activity', message, message_data, activity.summary, [activity.id], [], send_message, status)
                    MailMessage.sudo().create(vals)
                #msg = subject#_("Extra line with %s ") % (line.product_id.display_name,)
                activity.message_post(body=subject)
            except:
                #print ('==pass==')
                pass
            if activity.activity_whatsapp_counter < 5:
                activity.activity_whatsapp_counter += 1
            if activity_whatsapp_counter == 3:
                activity.activity_whatsapp_counter = 1
        return activity_employees
    
    # @api.model
    # def get_next_mail(self):
    #     last_notif_mail = fields.Datetime.to_string(self.env.context.get('lastcall') or fields.Datetime.now())
    #
    #     cron = self.env.ref('aos_whatsapp_activity.ir_cron_activity_send_user_reminder_1_wa', raise_if_not_found=False)
    #     if not cron:
    #         _logger.error("Cron for " + self._name + " can not be identified !")
    #         return False
    #
    #     interval_to_second = {
    #         "weeks": 7 * 24 * 60 * 60,
    #         "days": 24 * 60 * 60,
    #         "hours": 60 * 60,
    #         "minutes": 60,
    #         "seconds": 1
    #     }
    #
    #     if cron.interval_type not in interval_to_second:
    #         _logger.error("Cron delay can not be computed !")
    #         return False
    #
    #     cron_interval = cron.interval_number * interval_to_second[cron.interval_type]
    #
    #     all_meetings = self._get_next_potential_limit_alarm('email', seconds=cron_interval)
    #
    #     for meeting in self.env['calendar.event'].browse(all_meetings):
    #         max_delta = all_meetings[meeting.id]['max_duration']
    #
    #         if meeting.recurrency:
    #             at_least_one = False
    #             last_found = False
    #             for one_date in meeting._get_recurrent_date_by_event():
    #                 in_date_format = one_date.replace(tzinfo=None)
    #                 last_found = self.do_check_alarm_for_one_date(in_date_format, meeting, max_delta, 0, 'email', after=last_notif_mail, missing=True)
    #                 for alert in last_found:
    #                     self.do_mail_reminder(alert)
    #                     at_least_one = True  # if it's the first alarm for this recurrent event
    #                 if at_least_one and not last_found:  # if the precedent event had an alarm but not this one, we can stop the search for this event
    #                     break
    #         else:
    #             in_date_format = meeting.start
    #             last_found = self.do_check_alarm_for_one_date(in_date_format, meeting, max_delta, 0, 'email', after=last_notif_mail, missing=True)
    #             for alert in last_found:
    #                 self.do_mail_reminder(alert)
    #
    #
    # def do_mail_reminder(self, alert):
    #     meeting = self.env['calendar.event'].browse(alert['event_id'])
    #     alarm = self.env['calendar.alarm'].browse(alert['alarm_id'])
    #
    #     result = False
    #     if alarm.alarm_type == 'email':
    #         result = meeting.attendee_ids.filtered(lambda r: r.state != 'declined')._send_mail_to_attendees('calendar.calendar_template_meeting_reminder', force_send=True, force_event_id=meeting)
    #     return result
                    
    # assign_id = fields.Many2one(
    #     'res.users', 'Assigned',
    #     default=lambda self: self.env.user)
    # partner_id = fields.Many2one('res.partner', string='Partner')
    # mail_url = fields.Char(string="url", compute="_compute_url")
    # activity_status = fields.Char(string="status")
    # activity_feedback_email = fields.Char(string="feedback")
    #
    # def _compute_url(self):
    #     for activity in self:
    #         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #         static_url = "/web"
    #         view_id = "?db=%s#id=%s" % (self._cr.dbname, activity.res_id)
    #         view_type = "&view_type=form&model=%s" % (activity.res_model)
    #         mail_url_id = str(base_url) + static_url + view_id + view_type
    #         activity.update({
    #             'mail_url' : mail_url_id
    #         })
    #
    # @api.model
    # def create(self, values):
    #     activity = super(MailActivity, self).create(values)
    #     activity.write({'activity_status':'create'})
    #     return activity
    #
    # def action_create_calendar_event(self):
    #     self.action_close_dialog()
    #     activity = super(MailActivity, self).action_create_calendar_event()
    #     return activity
    #
    # def action_close_dialog(self):
    #     if self.activity_status != 'create':
    #         res_config_settings_obj = self.env['res.config.settings'].search([],limit=1,order="id desc")
    #         context = self._context
    #         current_uid = context.get('uid')
    #         user_id = self.env['res.users'].sudo().browse(current_uid)
    #         email_to = []
    #         email_to_assignee = []
    #         if user_id:
    #             if self.env.user.company_id.activity_email_notification == True:
    #                 if self.env.user.company_id.edit_notification == True:
    #                     if self.env.user.company_id.edit_create_user == True:
    #                         for user in self.create_user_id:
    #                             email_to.append(user.partner_id.id)
    #                         template_id = self.env['ir.model.data'].get_object_reference('bi_activity_mail_notification', 'email_template_edit_notification')[1]
    #                         email_template_obj = self.env['mail.template'].browse(template_id)
    #                         if self.summary:
    #                             body_html = '''
    #                             <div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
    #                                 <p>Dear <b>{0},</b></p><br/>
    #                                 <p>Your Scheduled Activity | {1} - {2} of document  {3} has been modified by {4}. </p><br/>
    #                                 <h4>Details:-</h4>
    #                                 <b>Summary: </b>{5}<br/></br>
    #                                 <b>Due date: </b>{7}<br/></br>
    #                                 <b>Description: </b>{6}
    #                             </div>
    #                             <br/>
    #                             <div style="margin: 16px 0px 16px 0px; font-size: 14px;">
    #                                 <a href='{8}'
    #                                 style="background-color:#875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px;">
    #                                 View <t t-esc="model_description or 'document'"/>
    #                                 </a>
    #                             </div>
    #                             '''.format(
    #                                 self.create_user_id.name, self.activity_type_id.name, self.summary,self.res_name,self.assign_id.name,self.summary,self.note,self.date_deadline,self.mail_url)
    #                         else:
    #                             body_html = '''
    #                             <div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
    #                                 <p>Dear <b>{0},</b></p><br/>
    #                                 <p>Your Scheduled Activity | {1} of document  {2} has been modified by {3}. </p><br/>
    #                                 <h4>Details:-</h4>
    #                                 <b>Summary: </b>{4}<br/></br>
    #                                 <b>Due date: </b>{6}<br/></br>
    #                                 <b>Description: </b>{5}
    #                             </div>
    #                             <br/>
    #                             <div style="margin: 16px 0px 16px 0px; font-size: 14px;">
    #                                 <a href='{7}'
    #                                 style="background-color:#875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px;">
    #                                 View <t t-esc="model_description or 'document'"/>
    #                                 </a>
    #                             </div>
    #                             '''.format(
    #                                 self.create_user_id.name, self.activity_type_id.name,self.res_name,self.assign_id.name,'',self.note,self.date_deadline,self.mail_url)
    #                         if template_id:
    #                             if self.id:
    #                                 values = email_template_obj.generate_email(self.id, fields=None)
    #                                 values['email_from'] = user_id.partner_id.email
    #                                 values['recipient_ids'] = [(4, pid) for pid in email_to]
    #                                 values['author_id'] = user_id.partner_id.id
    #                                 values['res_id'] = False
    #                                 values['model'] = False
    #                                 values['body_html'] = body_html
    #                                 mail_mail_obj = self.env['mail.mail']
    #                                 msg_id = mail_mail_obj.create(values)
    #                                 if msg_id:
    #                                     mail_mail_obj.send([msg_id])
    #                                     msg_id.sudo().send()
    #                     if self.env.user.company_id.edit_assignee_user == True:
    #                         for user in self.user_id:
    #                             email_to_assignee.append(user.partner_id.id)
    #                         if self.user_id.id != self.create_user_id.id or self.env.user.company_id.cancel_create_user == False:
    #                             template_id = self.env['ir.model.data'].get_object_reference('bi_activity_mail_notification', 'email_template_edit_notification_assignee')[1]
    #                             email_template_obj = self.env['mail.template'].browse(template_id)
    #                             if self.summary:
    #                                 body_html = '''
    #                                 <div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
    #                                     <p>Dear <b>{0},</b></p><br/>
    #                                     <p>Your Scheduled Activity | {1} - {2} of document  {3} has been modified by {4}. </p><br/>
    #                                     <h4>Details:-</h4>
    #                                     <b>Summary: </b>{5}<br/></br>
    #                                     <b>Due date: </b>{7}<br/></br>
    #                                     <b>Description: </b>{6}
    #                                 </div>
    #                                 <br/>
    #                                 <div style="margin: 16px 0px 16px 0px; font-size: 14px;">
    #                                     <a href='{8}'
    #                                     style="background-color:#875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px;">
    #                                     View <t t-esc="model_description or 'document'"/>
    #                                     </a>
    #                                 </div>
    #                                 '''.format(
    #                                     self.user_id.name, self.activity_type_id.name, self.summary,self.res_name,self.assign_id.name,self.summary,self.note,self.date_deadline,self.mail_url)
    #                             else:
    #                                 body_html = '''
    #                                 <div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
    #                                     <p>Dear <b>{0},</b></p><br/>
    #                                     <p>Your Scheduled Activity | {1} of document  {2} has been modified by {3}. </p><br/>
    #                                     <h4>Details:-</h4>
    #                                     <b>Summary: </b>{4}<br/></br>
    #                                     <b>Due date: </b>{6}<br/></br>
    #                                     <b>Description: </b>{5}
    #                                 </div>
    #                                 <br/>
    #                                 <div style="margin: 16px 0px 16px 0px; font-size: 14px;">
    #                                     <a href='{7}'
    #                                     style="background-color:#875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px;">
    #                                     View <t t-esc="model_description or 'document'"/>
    #                                     </a>
    #                                 </div>
    #                                 '''.format(
    #                                     self.user_id.name, self.activity_type_id.name,self.res_name,self.assign_id.name,'',self.note,self.date_deadline,self.mail_url)
    #
    #                             if template_id:
    #                                 if self.id:
    #                                     values = email_template_obj.generate_email(self.id, fields=None)
    #                                     values['email_from'] = user_id.partner_id.email
    #                                     values['recipient_ids'] = [(4, pid) for pid in email_to_assignee]
    #                                     values['author_id'] = user_id.partner_id.id
    #                                     values['res_id'] = False
    #                                     values['model'] = False
    #                                     values['body_html'] = body_html
    #                                     mail_mail_obj = self.env['mail.mail']
    #                                     msg_id = mail_mail_obj.create(values)
    #                                     if msg_id:
    #                                         mail_mail_obj.send([msg_id])
    #                                         msg_id.sudo().send()
    #     self.write({'activity_status':'write'})
    #     return {'type': 'ir.actions.act_window_close'}
    #
    # def action_feedback(self, feedback=False):
    #     self.write({'activity_feedback_email':feedback})
    #     res_config_settings_obj = self.env['res.config.settings'].search([],limit=1,order="id desc")
    #     context = self._context
    #     current_uid = context.get('uid')
    #     user_id = self.env['res.users'].sudo().browse(current_uid)
    #     email_to = []
    #     email_to_assignee = []
    #     if user_id:
    #         if self.env.user.company_id.activity_email_notification == True:
    #             if self.env.user.company_id.done_notification == True:
    #                 if self.env.user.company_id.done_create_user == True:
    #                     for user in self.create_user_id:
    #                         email_to.append(user.partner_id.id)
    #                     template_id = self.env['ir.model.data'].get_object_reference('bi_activity_mail_notification', 'email_template_done_notification')[1]
    #                     email_template_obj = self.env['mail.template'].browse(template_id)
    #                     if template_id:
    #                         if self.id:
    #                             values = email_template_obj.generate_email(self.id, fields=None)
    #                             values['email_from'] = user_id.partner_id.email
    #                             values['recipient_ids'] = [(4, pid) for pid in email_to]
    #                             values['author_id'] = user_id.partner_id.id
    #                             values['res_id'] = False
    #                             values['model'] = False
    #                             mail_mail_obj = self.env['mail.mail']
    #                             msg_id = mail_mail_obj.create(values)
    #                             if msg_id:
    #                                 mail_mail_obj.send([msg_id])
    #                                 msg_id.sudo().send()
    #                 if self.env.user.company_id.done_assignee_user == True:
    #                     for user in self.user_id:
    #                         email_to_assignee.append(user.partner_id.id)
    #                     if self.user_id.id != self.create_user_id.id or self.env.user.company_id.cancel_create_user == False:
    #                         template_id = self.env['ir.model.data'].get_object_reference('bi_activity_mail_notification', 'email_template_done_notification_assignee')[1]
    #                         email_template_obj = self.env['mail.template'].browse(template_id)
    #                         if template_id:
    #                             if self.id:
    #                                 values = email_template_obj.generate_email(self.id, fields=None)
    #                                 values['email_from'] = user_id.partner_id.email
    #                                 values['recipient_ids'] = [(4, pid) for pid in email_to_assignee]
    #                                 values['author_id'] = user_id.partner_id.id
    #                                 values['res_id'] = False
    #                                 values['model'] = False
    #                                 mail_mail_obj = self.env['mail.mail']
    #                                 msg_id = mail_mail_obj.create(values)
    #                                 if msg_id:
    #                                     mail_mail_obj.send([msg_id])
    #                                     msg_id.sudo().send()
    #     self.update({'activity_status':'done',})
    #     res = super(MailActivity, self).action_feedback()
    #
    #     return res
    #
    # def unlink(self):
    #     if self.activity_status != 'done' or self.activity_status == 'write':
    #         res_config_settings_obj = self.env['res.config.settings'].search([],limit=1,order="id desc")
    #         current_uid = self._uid
    #         user_id = self.env['res.users'].sudo().browse(current_uid)
    #         email_to = []
    #         email_to_assignee = []
    #         if user_id:
    #             if self.env.user.company_id.activity_email_notification == True:
    #                 if self.env.user.company_id.cancel_notification == True:
    #                     if self.env.user.company_id.cancel_create_user == True:
    #                         for user in self.create_user_id:
    #                             email_to.append(user.partner_id.id)
    #                         template_id = self.env['ir.model.data'].get_object_reference('bi_activity_mail_notification', 'email_template_cancel_notification')[1]
    #                         email_template_obj = self.env['mail.template'].browse(template_id)
    #                         if template_id:
    #                             if self.id:
    #                                 values = email_template_obj.generate_email(self.id, fields=None)
    #                                 values['email_from'] = user_id.partner_id.email
    #                                 values['recipient_ids'] = [(4, pid) for pid in email_to]
    #                                 values['author_id'] = user_id.partner_id.id
    #                                 values['res_id'] = False
    #                                 values['model'] = False
    #                                 mail_mail_obj = self.env['mail.mail']
    #                                 msg_id = mail_mail_obj.create(values)
    #                                 if msg_id:
    #                                     mail_mail_obj.send([msg_id])
    #                                     msg_id.sudo().send()
    #                     if self.env.user.company_id.cancel_assignee_user == True:
    #                         for user in self.user_id:
    #                             email_to_assignee.append(user.partner_id.id)
    #                         if self.user_id.id != self.create_user_id.id or self.env.user.company_id.cancel_create_user == False:
    #                             template_id = self.env['ir.model.data'].get_object_reference('bi_activity_mail_notification', 'email_template_cancel_notification_assignee')[1]
    #                             email_template_obj = self.env['mail.template'].browse(template_id)
    #                             if template_id:
    #                                 if self.id:
    #                                     values = email_template_obj.generate_email(self.id, fields=None)
    #                                     values['email_from'] = user_id.partner_id.email
    #                                     values['recipient_ids'] = [(4, pid) for pid in email_to_assignee]
    #                                     values['author_id'] = user_id.partner_id.id
    #                                     values['res_id'] = False
    #                                     values['model'] = False
    #                                     mail_mail_obj = self.env['mail.mail']
    #                                     msg_id = mail_mail_obj.create(values)
    #                                     if msg_id:
    #                                         mail_mail_obj.send([msg_id])
    #                                         msg_id.sudo().send()
    #     return super(MailActivity, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: