/** @odoo-module **/

import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";

export function generateSoundAlert(env, action) {
    if (action.params.sound_stream) {
        var audio = new window.Audio("data:audio/mp3;base64," + action.params.sound_stream);
        audio.currentTime = 0;
        audio.loop = false;
        audio.volume = 1;
        Promise.resolve(audio.play()).catch(()=>{})
    }
}

export const generateVoiceSoundAlert = {
    dependencies: ["bus_service", "notification"],
    start(env, { bus_service, notification: notificationService}) {
        bus_service.subscribe("voice_alert_sound", ({ sound_stream }) => {
            generateSoundAlert(env, {'params': {'sound_stream': sound_stream}});
        });
        bus_service.start();
    },
};

export function generateSoundAlert1(env, action) {
    console.log("test");
    env.services.rpc("/web/sign/get_fonts", {
        partner_id: 10
    });
}

registry.category("actions").add("generate_sound_alert", generateSoundAlert);
registry.category("services").add("generate_voice_alert", generateVoiceSoundAlert);