odoo.define('dynamic_portal.onchange_fields', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var rpc = require('web.rpc');

publicWidget.registry.onchangeFields = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(.card-header)',
    events: {
        'change input': '_onInputChange',
        'change select': '_onInputChange',
        'click .clear_file': '_HideButton',
    },

    _onInputChange(e) {
        let field_name = e.target.getAttribute('name');
    },

     _HideButton(e) {
        e.target.parentNode.parentNode.style.display = "none";

    },


    _onInputChange: function (e) {

        let field_name = e.target.getAttribute('name');
        let model_id = document.getElementById('model_id').value;


        rpc.query({
            model: 'portal.portal',
            method: 'get_form_fields',
            args: [parseInt(model_id)],
        }).then(function (result) {
            var dict = {};
            dict['id'] = document.getElementById('record_id').value;
            for (let i = 0; i < result.length; i++) {
                var field = result[i];
                let field_input = document.getElementById(field);
                if (field_input){
                    let field_value = field_input.value;
                    let type = document.getElementById(field).type;
                    if(type == 'select-multiple'){
                        field_value = document.getElementById(field).selectedOptions;
                        field_value = Array.from(field_value).map(({ value }) => value);
                    }
                    dict[field] = field_value;
                }
            }
            rpc.query({
            model: 'portal.portal',
            method: 'get_onchange_values',
            args: [parseInt(model_id),field_name,dict],
            }).then(function (result) {
                for (const [key, value] of Object.entries(result)) {
                    var input_field = document.getElementById(key);
                    if (Array.isArray(value)){
                        // delete tabel rows
                        var rowCount = input_field.rows.length;
                        for (var i = 0; i < rowCount-1; i++) {
                            input_field.deleteRow(1);
                        }
                        var values = value[0];
                        var list = value[1];
                        for (let j = 0; j < values.length; j++) {
                            var current_val =values[j]
    //                        console.log("current_val", current_val);
                            var currentRow = input_field.insertRow(-1);
                            for (let i = 0; i < list.length; i++) {
                                var list_fields = list[i];
                                var field_value = false;
                                if(list_fields['name'] in current_val){
                                    field_value = current_val[list_fields['name']]
                                }
                                if (list_fields['type'] != 'select'){
                                    var cell = document.createElement("input");
                                    name = key+"."+list_fields['name']+"."+-j;
                                    cell.setAttribute("name", name);
                                    cell.setAttribute("type", list_fields['type']);
                                    cell.setAttribute("value", field_value);
                                    cell.setAttribute("class", "form-control");
                                    var currentCell = currentRow.insertCell(-1);
                                    currentCell.appendChild(cell);
                                }
                                else{
                                    var selectList = document.createElement("select");
                                    selectList.id = "mySelect";
                                    name = key+"."+list_fields['name']+"."+-j;
                                    selectList.setAttribute("name", name);
                                    selectList.setAttribute("class", "form-control");
                                    var currentCell = currentRow.insertCell(-1);
                                    currentCell.appendChild(selectList);
                                    var array = list_fields['selection']
                                    for (var k = 0; k < array.length; k++) {
                                        var option = document.createElement("option");
                                        option.value = array[k]['key'];
                                        option.text = array[k]['val'];
                                        if (field_value == array[k]['key']){
                                            option.selected = 1;
                                        }
                                        selectList.appendChild(option);

                                    }
                                }
                            }
                            let btn = document.createElement("a");
                            btn.innerHTML = "<span style='color: red;font-size: 15px;' class='fa fa-trash'></span>";
                            var currentCell = currentRow.insertCell(-1);
                            currentCell.appendChild(btn);
                            btn.setAttribute("class", "o_delete_line");
                        }

                    }else{
//                        console.log("current_val", key,">", value);
                        input_field.setAttribute("value", value);
                    }

                }

            });


        });








    },


});

});
