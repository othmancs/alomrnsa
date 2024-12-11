odoo.define('dynamic_portal.onchange_buttons', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var rpc = require('web.rpc');

publicWidget.registry.portalOnchangeButtons = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(.card-header)',
    events: {
        'click .onchange_button': '_onChangeButton',
    },

    _onChangeButton: function (e) {

        let button = e.target.parentNode.getAttribute('id');
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
                dict[field] = document.getElementById(field).value;
            }
            rpc.query({
            model: 'portal.portal',
            method: 'get_onchange_values',
            args: [parseInt(model_id),button,dict],
            }).then(function (result) {
                for (const [table_id, value] of Object.entries(result)) {
                    var myTable = document.getElementById(table_id);
                    // delete tabel rows
                    var rowCount = myTable.rows.length;
                    for (var i = 0; i < rowCount-1; i++) {
                        myTable.deleteRow(1);
                    }
                    var values = value[0];
                    var list = value[1];
                    for (let j = 0; j < values.length; j++) {
                        var current_val =values[j]
//                        console.log("current_val", current_val);
                        var currentRow = myTable.insertRow(-1);
                        for (let i = 0; i < list.length; i++) {
                            var list_fields = list[i];
                            var field_value = false;
                            if(list_fields['name'] in current_val){
                                field_value = current_val[list_fields['name']]
                            }
                            console.log("field_value", field_value);
                            if (list_fields['type'] != 'select'){
                                var cell = document.createElement("input");
                                name = table_id+"."+list_fields['name']+"."+-j;
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
                                name = table_id+"."+list_fields['name']+"."+-j;
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
                }

            });


        });








    },


});

});
