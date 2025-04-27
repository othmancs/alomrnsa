odoo.define('mobile_responsive.mobile_adjustments', function (require) {
    "use strict";
    
    var utils = require('web.utils');
    
    function isMobileDevice() {
        return (typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1);
    }
    
    $(document).ready(function () {
        if (isMobileDevice()) {
            $('body').addClass('o_mobile_device');
            $('.o_form_view .oe_title').css('font-size', '1.2rem');
            $('.o_control_panel .btn').css({
                'padding': '6px 10px',
                'font-size': '13px'
            });
            $('.o_control_panel .o_cp_switch_buttons').addClass('d-none d-md-inline-block');
            if ($('.o_sub_menu').length) {
                $('.o_sub_menu .dropdown-item').css('font-size', '14px');
            }
        }
    });
    
    $(window).on('resize', utils.debounce(function () {
        if ($(window).width() < 768) {
            $('.o_list_view th').css('font-size', '12px');
        } else {
            $('.o_list_view th').css('font-size', '');
        }
    }, 200));
});