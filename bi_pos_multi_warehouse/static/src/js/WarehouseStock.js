odoo.define('warehouse_management.StockWarehouse', function(require) {
	'use strict';



	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');
	      
	var { pos_model, Orderline } = require('point_of_sale.models');  
	let location_id = null;

	

	class PosStockWarehouse extends AbstractAwaitablePopup {
		setup() {
			super.setup();
			this.product = this.props.product;
			this.result = this.props.result;
			this.locations = this.result || [];
			this.location_id = null;
		}
		
		cancel() {
			this.props.resolve({ confirmed: false, payload: null });
			this.showScreen('ProductScreen');
			this.env.posbus.trigger('close-popup', {
                popupId: this.props.id });
        
		
		}

		apply() {
			let self = this;
			let product = this.env.pos.db.get_product_by_id(this.product.id);
			let rec = this.props.rec;
			let entered_code = $("#entered_item_qty").val();
			let list_of_qty =$('.entered_item_qty');
			let order = this.env.pos.get_order();
			let warehouse = this.env.pos.pos_custom_location;
			let pos = self.env.pos
		
			$.each(list_of_qty, function(index, value) {
				let entered_item_qty =$(value).find('input');
				let qty_id = parseFloat(entered_item_qty.attr('qty-id'));;
				let loc_id = entered_item_qty.attr('locdbid');
				let loc_name = entered_item_qty.attr('loc-id');
				let entered_qty = parseFloat(entered_item_qty.val() || 0);
				let selectedOrder = self.env.pos.get_order();
				
			   	if(entered_qty > 0){
					if(qty_id >= entered_qty){
					  	if (entered_qty != 0){
					  		if(self.env.pos.config.stock_qty == 'qty_available'){
					  			product['bi_on_hand'] += entered_qty;
					  			
					  		}
					  		else{
					  			product.virtual_available -= entered_qty;
					  		}
						  	//order.add_product(product);
							let orderline = Orderline.create({}, {
			                        pos: self.env.pos,
			                        order: order,
			                        product: product,
			                        stock_location_id:warehouse
			                    });
					
						  	orderline.product=product;
							orderline.stock_location_id = loc_id;
							orderline.stock_location_name = loc_name
							orderline.set_quantity(entered_qty);
							order.add_orderline(orderline)
							self.showScreen('ProductScreen');
							self.env.posbus.trigger('close-popup', {popupId: self.props.id });

						}
					}
					else{
					   if(self.env.pos.config.Negative_selling){
						  if (entered_qty != 0){
						  		let orderline = Orderline.create({}, {
			                        pos: self.env.pos,
			                        order: order,
			                        product: product,
			                        stock_location_id:warehouse
			                    });
							  //let orderline = new pos_model.Orderline({},{pos:self.env.pos,order:order,product:product,stock_location_id:warehouse});
							  orderline.product=product;
							  orderline.stock_location_id = loc_id;
							  orderline.stock_location_name = loc_name
							  orderline.set_quantity(entered_qty);
							  order.add_orderline(orderline)
							  self.showScreen('ProductScreen');
							  self.env.posbus.trigger('close-popup', {popupId: self.props.id });

						  }
							  }
					   else{
							 let result = 'This Location has :' + qty_id +' QTY.  You have entered : '+ entered_qty;
							 self.showPopup('ErrorPopup', {
							 title: self.env._t('Please enter valid amount of quantity.'),
							 body: self.env._t(result),
							 });
						 }
					}
				}
			});
		}
	}

	PosStockWarehouse.template = 'PosStockWarehouse';
	PosStockWarehouse.defaultProps = {
		confirmText: 'Apply',
		cancelText: 'Cancel',
		title: 'Confirm ?',
		body: '',
	};

	Registries.Component.add(PosStockWarehouse);

	return PosStockWarehouse;
});
