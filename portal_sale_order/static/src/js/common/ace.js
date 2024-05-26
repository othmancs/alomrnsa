odoo.define('portal_sale_order.ace', function (require) {
    'use strict';

    var config = require('web.config');
    var Widget = require('web.Widget');
    var ViewEditor = require('web_editor.ace');

    var ViewEditorPortal = ViewEditor.include({
        _getSelectedResource: function () {
            var value = this.$lists[this.currentType].val();
            return parseInt(value, 10) || value;
        },

        _updateViewSelectDOM: function () {
            var currentId = this._getSelectedResource();

            var self = this;
            this.$lists.xml.empty();
            _.each(this.sortedViews, function (view) {
                self.$lists.xml.append($('<option/>', {
                    value: view.id,
                    text: view.name,
                    selected: currentId === view.id,
                    'data-level': view.level,
                    'data-debug': view.xml_id,
                }));
            });

            this.$lists.scss.empty();
            _populateList(this.sortedSCSS, this.$lists.scss, 5);

            this.$lists.js.empty();
            _populateList(this.sortedJS, this.$lists.js, 3);

            // Define a list of the elements you want to initialize
            const elements = ['xml', 'scss', 'js'];
            // Iterate over each element and apply the select2 configuration if the element exists
            elements.forEach(element => {
                if (this.$lists[element] && this.$lists[element].select2) {
                    try {
                        // Check if Select2 is initialized on the element before destroying it
                        if (this.$lists[element].data('select2')) {
                            this.$lists[element].select2('destroy');
                        }

                        // Initialize Select2 with the specified configurations
                        this.$lists[element].select2({
                            formatResult: _formatDisplay.bind(this, false),
                            formatSelection: _formatDisplay.bind(this, true),
                        });

                        // Add the class to the dropdown
                        var select2Instance = this.$lists[element].data('select2');
                        if (select2Instance && select2Instance.dropdown && select2Instance.dropdown.$dropdown) {
                            select2Instance.dropdown.$dropdown.addClass('o_ace_select2_dropdown');
                        }
                    } catch (e) {
                        console.error(`Error initializing Select2 on ${element}:`, e);
                    }
                }
            });

            function _populateList(sortedData, $list, lettersToRemove) {
                _.each(sortedData, function (bundleInfos) {
                    var $optgroup = $('<optgroup/>', {
                        label: bundleInfos[0],
                    }).appendTo($list);
                    _.each(bundleInfos[1], function (dataInfo) {
                        var name = dataInfo.url.substring(_.lastIndexOf(dataInfo.url, '/') + 1, dataInfo.url.length - lettersToRemove);
                        $optgroup.append($('<option/>', {
                            value: dataInfo.url,
                            text: name,
                            selected: currentId === dataInfo.url,
                            'data-debug': dataInfo.url,
                            'data-customized': dataInfo.customized
                        }));
                    });
                });
            }

            function _formatDisplay(isSelected, data) {
                var $elem = $(data.element);

                var text = data.text || '';
                if (!isSelected) {
                    text = Array(($elem.data('level') || 0) + 1).join('-') + ' ' + text;
                }
                var $div = $('<div/>', {
                    text: text,
                    class: 'o_ace_select2_result',
                });

                if ($elem.data('dirty') || $elem.data('customized')) {
                    $div.prepend($('<span/>', {
                        class: 'mr8 fa fa-floppy-o ' + ($elem.data('dirty') ? 'text-warning' : 'text-success'),
                    }));
                }

                if (!isSelected && config.isDebug() && $elem.data('debug')) {
                    $div.append($('<span/>', {
                        text: ' (' + $elem.data('debug') + ')',
                        class: 'ml4 small text-muted',
                    }));
                }

                return $div;
            }
        },
    });

    return ViewEditorPortal;
});
