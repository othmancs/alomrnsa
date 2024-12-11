odoo.define('dynamic_portal.edit_one2many_lines', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var rpc = require('web.rpc');

publicWidget.registry.editOne2many = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(.table-responsive)',
    events: {
        'click .o_add_lines': '_onAddCode',
        'click .o_delete_line': '_onDeleteClick',
    },

    _onDeleteClick: function (e) {
        e.target.parentNode.parentNode.parentNode.parentNode.removeChild(e.target.parentNode.parentNode.parentNode);
    },


    _onAddCode: function (e) {
        let table_id = e.target.parentNode.getAttribute('id');
        let model_id = e.target.parentNode.getAttribute('name');
        var myTable = document.getElementById(table_id);
        var currentIndex = myTable.rows.length;
        var currentRow = myTable.insertRow(-1);

        rpc.query({
                model: 'portal.portal',
                method: 'get_lines',
                 args: [parseInt(model_id),table_id],
            }).then(function (list) {
                for (let i = 0; i < list.length; i++) {
                    if ( list[i]['type'] != 'select'){
                        var cell = document.createElement("input");
                        name = table_id+"."+list[i]['name']+"."+-currentIndex;
                        cell.setAttribute("name", name);
                        cell.setAttribute("type", list[i]['type']);
                        cell.setAttribute("class", "form-control");
                        var currentCell = currentRow.insertCell(-1);
                        currentCell.appendChild(cell);
                    }
                    else{
                        var selectList = document.createElement("select");
                        selectList.id = "mySelect";
                        name = table_id+"."+list[i]['name']+"."+-currentIndex;
                        selectList.setAttribute("name", name);
                        selectList.setAttribute("class", "form-control");
                        var currentCell = currentRow.insertCell(-1);
                        currentCell.appendChild(selectList);
                        var array = list[i]['selection']
                        for (var j = 0; j < array.length; j++) {
                            var option = document.createElement("option");
                            option.value = array[j]['key'];
                            option.text = array[j]['val'];
                            selectList.appendChild(option);
                        }
                    }
                }
                let btn = document.createElement("a");
                btn.innerHTML = "<span style='color: red;font-size: 15px;' class='fa fa-trash'></span>";
                var currentCell = currentRow.insertCell(-1);
                currentCell.appendChild(btn);
                btn.setAttribute("class", "o_delete_line");
            })

    },


});

});
