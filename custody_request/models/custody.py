# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class CustodyRequest(models.Model):
    _inherit = "custody.request"

    custody_approval_route = fields.Selection(related='company_id.custody_approval_route',
                                               string="Use Approval Route", readonly=True)
    state = fields.Selection([('draft','Draft'),
                              ('sent','Sent'),
                              ('to approve','Under Approval'),
                              ('sale','Approved'),
                              ('done','Posted'),
                              ('cancel','Rejected')],default='draft')
    team_custom_id = fields.Many2one(
        comodel_name="custody.team.custom",required=True, string="Custody Team", domain="[('company_id', '=', company_id)]",
        readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, ondelete="restrict"
    )

    approver_ids = fields.One2many(
        comodel_name="custody.order.approver", inverse_name="order_id", string="Approvers", readonly=True)

    current_approver = fields.Many2one(
        comodel_name="custody.order.approver", string="Approver",
        compute="_compute_approver", store=True, compute_sudo=True)

    next_approver = fields.Many2one(
        comodel_name="custody.order.approver", string="Next Approver",
        compute="_compute_approver", store=True, compute_sudo=True)

    is_current_approver = fields.Boolean(
        string="Is Current Approver", compute="_compute_is_current_approver"
    )

    lock_amount_total = fields.Boolean(
        string="Lock Amount Total", compute="_compute_lock_amount_total"
    )

    amount_total = fields.Monetary(tracking=True)

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'amount_total' in init_values and self.amount_total != init_values.get('amount_total'):
            self._check_lock_amount_total()
        return super(CustodyRequest, self)._track_subtype(init_values)

    def button_approve(self, force=False):
        for order in self:
            if not order.team_custom_id:
                # Do default behaviour if SO Team is not set
                super(CustodyRequest, order).button_approve(force)
            elif order.current_approver:
                if order.current_approver.user_id == self.env.user or self.env.is_superuser():
                    # If current user is current approver (or superuser) update state as "approved"
                    order.current_approver.state = 'approved'
                    order.message_post(body=_('Custody approved by %s') % self.env.user.name)
                    # Check is there is another approver
                    if order.next_approver:
                        # Send request to approve is there is next approver
                        order.send_to_approve()
                    else:
                        # If there is not next approval, than assume that approval is finished and send notification
                        partner = order.user_id.partner_id if order.user_id else order.create_uid.partner_id
                        order.message_post_with_view(
                            'custody_request.order_approval',
                            subject=_('Petty Cash Approved: %s') % (order.name,),
                            composition_mode='mass_mail',
                            partner_ids=[(4, partner.id)],
                            auto_delete=True,
                            auto_delete_message=True,
                            parent_id=False,
                            subtype_id=self.env.ref('mail.mt_note').id)
                        # Do default behaviour to set state as "sale" and update date_approve
                        return super(CustodyRequest, order).confirm_post()

    def confirm_dm(self):
        for order in self:
            # if order.state not in ['draft', 'sent']:
            #     continue

            if not order.team_custom_id:
                # Do default behaviour if SO Team is not set
                super(CustodyRequest, order).confirm_post()
            else:
                # Generate approval route and send SO to approve
                # raise ValidationError('hhhhhh')
                order.generate_approval_route()
                if order.next_approver:
                    # If approval route is generated and there is next approver mark the order "to approve"
                    order.write({'state': 'to approve'})
                    # And send request to approve
                    order.send_to_approve()
                else:
                    # If there are not approvers, do default behaviour and move SO to the "sale Order" state
                    super(CustodyRequest, order).button_approve()

            # order._add_supplier_to_product()
            if order.user_name.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.user_name.partner_id.id])
        return True

    def generate_approval_route(self):
        """
        Generate approval route for order
        :return:
        """
        for order in self:
            if not order.team_custom_id:
                continue
            if order.approver_ids:
                # reset approval route
                order.approver_ids.unlink()
            for team_approver in order.team_custom_id.approver_ids:

                custom_condition = order.compute_custom_condition(team_approver)
                if not custom_condition:
                    # Skip approver, if custom condition for the approver is set and the condition result is not True
                    continue

                min_amount = team_approver.company_currency_id._convert(
                    team_approver.min_amount,
                    order.currency_id,
                    order.company_id,
                    order.custody_date or fields.Date.today())
                if min_amount > order.amount_total:
                    # Skip approver if Minimum Amount is greater than Total Amount
                    continue
                max_amount = team_approver.company_currency_id._convert(
                    team_approver.max_amount,
                    order.currency_id,
                    order.company_id,
                    order.custody_date or fields.Date.today())
                if max_amount and max_amount < order.amount_total:
                    # Skip approver if Maximum Amount is set and less than Total Amount
                    continue

                # Add approver to the SO
                # raise ('jjjjjjjjjjj')
                self.env['custody.order.approver'].create({
                    'sequence': team_approver.sequence,
                    'team_custom_id': team_approver.team_custom_id.id,
                    'user_id': team_approver.user_id.id,
                    'role': team_approver.role,
                    'min_amount': team_approver.min_amount,
                    'max_amount': team_approver.max_amount,
                    'lock_amount_total': team_approver.lock_amount_total,
                    'order_id': order.id,
                    'team_approver_id': team_approver.id,
                })

    def compute_custom_condition(self, team_approver):
        self.ensure_one()
        localdict = {'SO': self, 'USER': self.env.user}
        if not team_approver.custom_condition_code:
            return True
        try:
            safe_eval(team_approver.custom_condition_code, localdict, mode='exec', nocopy=True)
            return bool(localdict['result'])
        except Exception as e:
            raise UserError(_('Wrong condition code defined for %s. Error: %s') % (team_approver.display_name, e))

    @api.depends('approver_ids.state')
    def _compute_approver(self):
        for order in self:
            next_approvers = order.approver_ids.filtered(lambda a: a.state == "to approve")
            order.next_approver = next_approvers[0] if next_approvers else False

            current_approvers = order.approver_ids.filtered(lambda a: a.state == "pending")
            order.current_approver = current_approvers[0] if current_approvers else False

    @api.depends('current_approver')
    def _compute_is_current_approver(self):
        for order in self:
            order.is_current_approver = ((order.current_approver and order.current_approver.user_id == self.env.user)
                                         or self.env.is_superuser())

    @api.depends('approver_ids.state', 'approver_ids.lock_amount_total')
    def _compute_lock_amount_total(self):
        for order in self:
            order.lock_amount_total = len(order.approver_ids.filtered(lambda a: a.state == "approved" and a.lock_amount_total)) > 0

    def send_to_approve(self):
        for order in self:
            if order.state != 'to approve' and not order.team_custom_id:
                continue

            main_error_msg = _("Unable to send approval request to next approver.")
            if order.current_approver:
                reason_msg = _("The order must be approved by %s") % order.current_approver.user_id.name
                raise UserError("%s %s" % (main_error_msg, reason_msg))

            if not order.next_approver:
                reason_msg = _("There are no approvers in the selected Custody team.")
                raise UserError("%s %s" % (main_error_msg, reason_msg))
            # use sudo as sale user cannot update sale.order.approver
            order.sudo().next_approver.state = 'pending'
            # Now next approver became as current
            current_approver_partner = order.current_approver.user_id.partner_id
            if current_approver_partner not in order.message_partner_ids:
                order.message_subscribe([current_approver_partner.id])
            order.with_user(order.user_id).message_post_with_view(
                'custody_request.request_to_approve_so',
                subject=_('Petty cash Approval: %s') % (order.name,),
                composition_mode='mass_mail',
                partner_ids=[(4, current_approver_partner.id)],
                auto_delete=True,
                auto_delete_message=True,
                parent_id=False,
                subtype_id=self.env.ref('mail.mt_note').id)

    def _check_lock_amount_total(self):
        msg = _('Sorry, you are not allowed to change Amount Total of SO. ')
        for order in self:
            if order.state in ('draft', 'sent'):
                continue
            if order.lock_amount_total:
                reason = _('It is locked after received approval. ')
                raise UserError(msg + "\n\n" + reason)
            if order.team_custom_id.lock_amount_total:
                reason = _('It is locked after generated approval route. ')
                suggestion = _('To make changes, cancel and reset Custody to draft. ')
                raise UserError(msg + "\n\n" + reason + "\n\n" + suggestion)