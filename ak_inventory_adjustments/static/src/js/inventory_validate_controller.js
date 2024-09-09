odoo.define('ak_inventory_adjustments.inventory_validate_controller', function (require) {
"use strict";
var core = require('web.core');
var qweb = core.qweb;
var _t = core._t;
var ListController = require('web.ListController');
var ListView = require('web.ListView');
var viewRegistry = require('web.view_registry');
var TreeButton = ListController.extend({
   buttons_template: 'ak_inventory_adjustments.buttons',
   events: _.extend({}, ListController.prototype.events, {
       'click .button_validate_inventory': '_ValidateInventory',
   }),
   init: function (parent, model, renderer, params) {
        var context = renderer.state.getContext();
        this.inventory_id = context.active_id;
        this._super.apply(this, arguments);
    },
   _ValidateInventory: function () {
        var self = this;
        var prom = Promise.resolve();
        var recordID = this.renderer.getEditableRecordID();
        if (recordID) {
            // If user's editing a record, we wait to save it before to try to
            // validate the inventory.
            prom = this.saveRecord(recordID);
        }
        prom.then(function () {
            self._rpc({
                model: 'stock.inventory',
                method: 'action_validate',
                args: [self.inventory_id]
            }).then(function (res) {
                if(res){
                    var exitCallback = function (infos) {
                        // In case we discarded a wizard, we do nothing to stay on
                        // the same view...
                        if (infos && infos.special) {
                            return;
                        }
                        // ... but in any other cases, we go back on the inventory form.
                        self.displayNotification({
                            type: 'warning',
                            message: "The inventory has been validated",
                            sticky: false
                            });
                        self.trigger_up('history_back');
                    };

                    if (_.isObject(res)) {
                        self.do_action(res, { on_close: exitCallback });
                    } else {
                        return exitCallback();
                    }
                }
                else{
                    self.trigger_up('history_back');
                }
            });
        });
       }
    });
    var InputListView = ListView.extend({
       config: _.extend({}, ListView.prototype.config, {
           Controller: TreeButton,
       }),
    });
    viewRegistry.add('button_in_tree', InputListView);
});
