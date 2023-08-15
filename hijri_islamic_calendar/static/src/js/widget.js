/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useInputField } from "@web/views/fields/input_field_hook";
import time from 'web.time';
var translation = require('web.translation');
var _t = translation._t;

const hijri_year_limit = 9;

const { Component,useRef} = owl;

export class FieldDateHijriWidget extends Component {
    static template = 'FieldDateHijriWidget'

    setup(){

        super.setup();

        this.input_result = useRef('date_hidden')
        this.input_result_temp = useRef('date_temp_hidden')
        this.hijri_wrap_div = useRef('hijri_wrap_div')
        this.hijri_year_selection = useRef('hijri-year-selection')
        this.hijri_month_selection = useRef('hijri-month-selection')
        this.hijri_day_selection = useRef('hijri-day-selection')

        this.hijri_year_cell_1_1 = useRef('hijri_year_cell_1_1')
        this.hijri_year_cell_1_2 = useRef('hijri_year_cell_1_2')
        this.hijri_year_cell_1_3 = useRef('hijri_year_cell_1_3')

        this.hijri_year_cell_2_1 = useRef('hijri_year_cell_2_1')
        this.hijri_year_cell_2_2 = useRef('hijri_year_cell_2_2')
        this.hijri_year_cell_2_3 = useRef('hijri_year_cell_2_3')

        this.hijri_year_cell_3_1 = useRef('hijri_year_cell_3_1')
        this.hijri_year_cell_3_2 = useRef('hijri_year_cell_3_2')
        this.hijri_year_cell_3_3 = useRef('hijri_year_cell_3_3')

        this.input_d = useRef('input_d')
        this.input_m = useRef('input_m')
        this.input_y = useRef('input_y')

        useInputField({ getValue: () => this.props.value || "", refName: "date_hidden" });

    }

    get_data_temp(vals){
        var data  = JSON.parse(this.input_result_temp.el.value || "{}");
        return data;
    }

    set_data_temp(vals){
        var data  = JSON.parse(this.input_result_temp.el.value || "{}");
        data = Object.assign({}, data, vals)
        this.input_result_temp.el.value = JSON.stringify(data)
    }

    deploy_hijri_year(){
        var data = this.get_data_temp();
        var year_start = this.get_year_start();

         let value = year_start;
         for(let row=1;row<=3;row++){
            for(let col=1;col<=3;col++){
                let ref = 'hijri_year_cell_'+row+'_'+col;
                this[ref].el.innerHTML = value;
                this[ref+'_value'] = value;
                value+=1;
            }
         }



    }

    get_year_start(){
          var data = this.get_data_temp();
          var hijri_year = new Date().getFullYear()-579;
          return data.year_start || hijri_year-5;
    }
    change_year_list(mode){
        if(mode=='prev'){
            var new_start = this.get_year_start() - hijri_year_limit;
            this.set_data_temp({year_start:new_start});
        }
        if(mode=='next'){
            var new_start = this.get_year_start() + hijri_year_limit;
            this.set_data_temp({year_start:new_start});
        }

        this.deploy_hijri_year();
    }


    split_hijri(value) {
        if(value){
                var day = value.split("/")[0].trim();
                var month = value.split("/")[1].trim();
                var year = value.split("/")[2].trim();
        }else{
                var day = "";
                var month = "";
                var year = "";
        }
        return {day:day, month:month, year:year}
    }

    format_hijri(day, month, year){
        if(!day | !month | !year ){
            return ""
        }
        return "".concat(day, " / ", month, " / ", year);
    }

    get_hijri_value(){
       var day = this.input_d.el.value;
       var month = this.input_m.el.value;
       var year = this.input_y.el.value;
       var val = this.format_hijri(day, month, year)
       return val || "";
    }


    _toggle_display(){

       if(this.hijri_wrap_div.el.hidden){
          this.hijri_wrap_div.el.hidden = false;
          this.hijri_year_selection.el.hidden = false;


       }else{
          this.hijri_wrap_div.el.hidden = true;
          this.hijri_year_selection.el.hidden = true;
       }

       this.hijri_month_selection.el.hidden = true;
       this.hijri_day_selection.el.hidden = true;

       this.deploy_hijri_year()


    }

    _on_click_clear(){
        this.update_final_result("")
    }
    _on_click_close(){
        this._toggle_display();
    }
    _on_click_input(){
        this._toggle_display();
    }

    _set_year(row, col){
        let year = this['hijri_year_cell_'+row+'_'+col+'_value'];
        this._update_state({year:year,state:"month"});
    }

    _set_month(month){
        this._update_state({month:month,state:"day"})
    }

    _set_day(day){
        this._update_state({day:day, state:"done"})

    }

    _update_state(vals){

        this.set_data_temp(vals);
        let data = this.get_data_temp();

        if(data.state == "month"){
            this.hijri_year_selection.el.hidden = true;
            this.hijri_month_selection.el.hidden = false;
            this.hijri_day_selection.el.hidden = true;
        }
        if(data.state == "day"){
            this.hijri_year_selection.el.hidden = true;
            this.hijri_month_selection.el.hidden = true;
            this.hijri_day_selection.el.hidden = false;
        }
        if(data.state == "done"){
            this.update_final_result();

        }

    }

    update_final_result(value){
        var data = this.get_data_temp();
        this.input_result.el.value = value || this.format_hijri(data.day, data.month, data.year);
        this.props.update(this.input_result.el.value.replace(FieldDateHijriWidget, ''));
        this.hijri_wrap_div.el.hidden = true;
    }


}


registry.category("fields").add("date_hijri", FieldDateHijriWidget);

