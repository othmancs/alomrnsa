/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import core from 'web.core';

registerPatch({
    name: 'Chatter',
    recordMethods: {
        // onClickSendWhatsapp(event) {
        //     core.bus.trigger("openMainPalette", {
        //         searchValue: "?",
        //     });
        // },
        onClickSendWhatsapp() {
            // const data2 = this._super(data);
            // const data = this._super;
            // const partner_ids = this.thread.args[1] || this.thread.kwargs.partner_ids;
            // const followers = data.getRecords('mail.followers', [
            //     ['res_model', '=', this.thread.model],
            //     ['res_id', 'in', this.thread.ids],
            //     ['partner_id', 'in', partner_ids || []],
            // ]);
            // const followers = this.thread.fetchData(['followers'])
            // const requestData = ['activities', 'followers', 'suggestedRecipients'];
            // if (this.hasMessageList) {
            //     requestData.push('attachments', 'messages');
            // }
            // const request = this.thread.fetchData(requestData);
            // this.chatterOwner.thread.followers.map(follower => ({ follower }));
            // console.log('==model==',this.thread.followers.map(follower => follower.partner.id))
            // console.log('==followers==',this.thread.model,this.thread.id,this,this.thread.followers)
            console.log('==messaging==',this.thread.model,this.thread.id,this.thread.id)
            const partner_ids = this.thread.followers.map(follower => follower.partner.id)
            const action = {
                type: 'ir.actions.act_window',
                res_model: 'whatsapp.compose.message',
                view_mode: 'form',
                views: [[false, 'form']],
                name: this.env._t("Send Whatsapp"),
                target: 'new',
                context: {
                    active_ids: [this.thread.id],
                    active_model: this.thread.model,
                    // default_res_id: this.thread.id,
                    default_subject: this.thread.name,
                    default_partner_ids: partner_ids,
                    // default_phone: this.thread.record.data[this.thread.name],
                },
            };
            this.env.services.action.doAction(
                action,
                {
                    onClose: async () => {
                        // this.thread.record.load();
                        // this.thread.record.model.notify();
                        if (!this.exists() && !this.thread) {
                            return;
                        }
                        this.reloadParentView();
                        // await this.thread.fetchData(['followers']);
                        // if (this.exists() && this.hasParentReloadOnFollowersUpdate) {
                        //     this.reloadParentView();
                        // }
                    },
                }
            );
        },
    },
});
