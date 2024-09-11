odoo.define('saudi_hr_it_operations.contact_form_view', function (require) {
    "use strict";

    var FormView = require('web.FormView');
    var FormController = require('web.FormController');
    var FormRenderer = require('web.FormRenderer');
    var view_registry = require('web.view_registry');

    var HRFormITOperationsRenderer = FormRenderer.extend({
        _renderButtonBoxNbButtons: function () {
            this._super.apply(this, arguments);
            return 50;
        }
    });

    var HRFormITOperationsView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Renderer: HRFormITOperationsRenderer,
            Controller: FormController,
        })
    });
    
    view_registry.add('saudi_hr_it_operations_form_view', HRFormITOperationsView);
});
