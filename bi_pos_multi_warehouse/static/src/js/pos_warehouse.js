/** @odoo-module **/

import ProductScreen from 'point_of_sale.ProductScreen';
import Registries from 'point_of_sale.Registries';
import { useBarcodeReader } from 'point_of_sale.custom_hooks';

export const CustomProductScreen = (ProductScreen) =>
    class extends ProductScreen {

        setup() {
            super.setup();
        }
		async _clickProduct(event) {
			let self = this;
			const product = event.detail;
            product['bi_on_hand'] = 0;
		    let order = self.env.pos.get_order();
            let location = self.env.pos.config.warehouse_ids;
            let partner_id = order.get_partner();
            let lines = order.get_orderlines();
            let warehouse = self.env.pos.pos_custom_location;
            let session = self.env.pos.config.stock_qty
            let config_loc = self.env.pos.config.default_location_src_id[0];
            let loc_qty = self.env.pos.prod_with_quant[product.id];
            let config_loc_qty = loc_qty[config_loc] || 0;
            let rec = 0;
            if (product.type == 'product'  && self.env.pos.config.pos_stock){
				let products = order.calculate_prod_qty();
				if(config_loc_qty > 0 || self.env.pos.config.Negative_selling ||  self.env.pos.config.stock_qty){
                    await this.rpc({
                        model: 'stock.quant',
                        method: 'warehouse_qty',
                        args:[partner_id, warehouse, product.id, session],
                    }).then(function(output){
                        if (lines.length > 0){
                            for (let i in output){
                                $.each(output[i], function( k, v ){
                                    if (k=='location'){
                                        if (products[v]){
                                            let found = $.grep(products[v], function(q) {
                                                if (q['name'] == product.display_name){
                                                    output[i]['quantity'] = output[i]['quantity'] - q['qty']
                                                }
                                            });
                                        }
                                    }
                                })   
                            }
                            rec = output;
                        }
                        else{
                            rec = output;
                        }
                    });
                    order.set_loaded_qty(rec)
                    await this.showPopup('PosStockWarehouse', {
                        'product': product,
                        'rec':rec,
                    });
                }else{
                    self.showPopup('ErrorPopup', {
                        'title': self.env._t('Out of Stock'),
                        'body':  self.env._t('Quantity is not available'),
                    });
                }
            }
            else {
                super._clickProduct(event);
            }
        }

        async _onClickPay() {
            var self = this;
            let order = this.env.pos.get_order();
            let products_data = order.calculate_prod_qty()
            let lines = order.get_orderlines();
            let pos_config = self.env.pos.config; 
            let allow_order = pos_config.Negative_selling;
            let call_super = true;
            if(pos_config.pos_stock){
                let prod_used_qty = {};
                $.each(lines, function( i, line ){
                    let locations = self.env.pos.locations;
                    let prd = line.product;
                    let loc_onhand = JSON.parse(prd.quant_text);
                    locations = locations.filter(function(item){
                        return item.warehouse_id[1] == line.stock_location_name
                    })
                    
                    if (prd.type == 'product'){
                        let loc_onhand = JSON.parse(prd.quant_text);
                        $.each(loc_onhand, function( k, v ){
                            _.each(locations,function(location){
                                if(location.id == k){
                                    var final_data = products_data[location.warehouse_id[1]]
                                    _.each(final_data,function(data){
                                        if(location.warehouse_id[1] == data.loc && data['id'] == prd.id){
                                            data['qty'] = v[0];
                                        }
                                    })
                                }
                            })
                        })
                        
                    }
                });
                $.each(products_data, function( product ){
                    var found = products_data[product]
                    _.each(found,function(data){
                        if (allow_order == false && data['qty'] < data['prod_qty']){
                            call_super = false;
                            self.showPopup('ErrorPopup', {
                                title: self.env._t('Deny Order'),
                                body: self.env._t("Deny Order" + "(" + data['name'] + ")" + " is Out of Stock."),
                            });
                        }
                    })
                    
                    
                });
            }
            if(call_super){
                super._onClickPay();
            }
        }
    };

Registries.Component.extend(ProductScreen, CustomProductScreen);



