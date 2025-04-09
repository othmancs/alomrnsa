odoo.define('customer_statement.report', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');

var CustomerStatementReport = Widget.extend({
    events: {
        'click .o_report_move_link': '_onClickMoveLink',
    },

    _onClickMoveLink: function (ev) {
        ev.preventDefault();
        var moveId = $(ev.currentTarget).data('move-id');
        if (moveId) {
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'حركة',
                res_model: 'account.move',
                res_id: moveId,
                views: [[false, 'form']],
                target: 'current',
            });
        }
    },
});

core.action_registry.add('customer_statement_report', CustomerStatementReport);

return CustomerStatementReport;

});