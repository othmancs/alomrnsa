odoo.define('saudi_hr.employee_form_view', function (require) {
    "use strict";

    var FormView = require('web.FormView');
    var FormController = require('web.FormController');
    var FormRenderer = require('web.FormRenderer');
    var view_registry = require('web.view_registry');

    var HRFormRenderer = FormRenderer.extend({
        _renderButtonBoxNbButtons: function () {
            this._super.apply(this, arguments);
            return 50;
        }
    });

    var HRFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Renderer: HRFormRenderer,
            Controller: FormController,
        })
    });
    
    view_registry.add('saudi_hr_form_view', HRFormView);
});
