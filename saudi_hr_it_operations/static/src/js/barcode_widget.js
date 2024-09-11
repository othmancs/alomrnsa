odoo.define("essex_weld_custom_view.barcode_widget_equipment", function(require) {
    "use strict";

    var FieldRegistry = require('web.field_registry');
    var core = require("web.core");
    var Widget = require('web.Widget');
    var widgetRegistry = require('web.widget_registry');
    var Barcode128Widget = require('barcode_widget.form_widgets');

    var Barcode128WidgetEquipment = Barcode128Widget.extend({

        init: function(parent, options){
            // To set the barcode value in variable
            this._super.apply(this, arguments);
            this.barcode = options.data.serial_no;
        },
    });
    widgetRegistry.add('BarCode128Equipment', Barcode128WidgetEquipment);
    return Barcode128WidgetEquipment;
});
