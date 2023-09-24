odoo.define('bi_pos_multi_warehouse.ProductsWidget', function(require) {
	"use strict";


	const Registries = require('point_of_sale.Registries');
	const ProductsWidget = require('point_of_sale.ProductsWidget');

	let prd_list_count = 0;

	const WarehouseProductsWidget = (ProductsWidget) =>
		class extends ProductsWidget {
			setup() {
				super.setup();
			}

			get productsToDisplay() {
				let self = this;
				let prods = super.productsToDisplay;
				let order = self.env.pos.get_order();
               if (self.env.pos.config.pos_stock){
                	
					let prod_ids = [];
					$.each(prods, function( i, prd ){
						prod_ids.push(prd.id)
					});
					let locations = self.env.pos.locations;
					if(self.env.pos.config.stock_qty == 'qty_available'){
						$.each(prods, function( i, prd ){
							prd['qty_available'] = 0;
							let qty_value=0
							let loc_onhand = JSON.parse(prd.quant_text);
							let warehouse = self.env.pos.pos_custom_location;
							_.each(locations,function(location){
								for (const [key, value] of Object.entries(loc_onhand)) {
									  if(location.id == key){
									  	qty_value=qty_value+value[0]
									}
								}
							})
							if(prd['bi_on_hand']>0){
								prd['bi_on_hand'] = order.get_display_product_qty(prd)
								prd['qty_available'] = qty_value - prd['bi_on_hand']
							}
							else{
								if(order){
									var reserved_qty = order.get_display_product_qty(prd);	
									prd['qty_available'] = qty_value - reserved_qty;
								}
								else{
									prd['qty_available']=qty_value
								}
							}
						});
					}
					else{
						$.each(prods, function( i, prd ){
							let loc_available = JSON.parse(prd.quant_text);
							prd['virtual_available'] = 0;
							let total = 0;
							_.each(locations,function(location){
								$.each(loc_available, function( k, v ){
									if(location.id == k){
										total += v[0];
									}
								})
							})
							let out_qty = prd['outgoing_qty']
							let final_data = total - out_qty;
							prd['virtual_available'] = final_data;
						});
					}
				}

	            if (this.searchWord !== '') {
	                return this.env.pos.db.search_product_in_category(
	                    this.selectedCategoryId,
	                    this.searchWord
	                );
	            } else {
	                return this.env.pos.db.get_product_by_category(this.selectedCategoryId);
	            }
	        }
		};

	Registries.Component.extend(ProductsWidget, WarehouseProductsWidget);

	return ProductsWidget;

});







