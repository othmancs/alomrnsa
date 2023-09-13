odoo.define('warehouse_managment.pos_models', function(require){
"use strict";

	

	//models.load_fields('product.product', ['type','quant_text','qty_available','incoming_qty','outgoing_qty','virtual_available']);
	var { PosGlobalState, Order, Orderline, models } = require('point_of_sale.models');
	const Registries = require('point_of_sale.Registries');


	const PosHomePosGlobalState = (PosGlobalState) => class PosHomePosGlobalState extends PosGlobalState {
		async _processData(loadedData) {
			await super._processData(...arguments);
			let self = this;
			// self.pos_product_pack = loadedData['product.product'];
			self.prod_with_quant = loadedData['prod_with_quant'];
			self.pos_custom_location = loadedData['pos_custom_location'];
			self.loc_by_id = loadedData['loc_by_id'];
			self.locations = loadedData['locations'];
		}
	}
	Registries.Model.extend(PosGlobalState, PosHomePosGlobalState);
		// models.load_models({
		// 	model: 'product.product',
		// 	fields: ['name','type','quant_text'],
		// 	domain: null,
		// 	loaded: function(self, prods) {
		// 		self.prods = prods;
		// 		self.prod_with_quant = {};
		// 		prods.forEach(function(prd) {
		// 			prd.all_qty = JSON.parse(prd.quant_text);
		// 			self.prod_with_quant[prd.id] = prd.all_qty;

		// 		});
		// 	},
		// });



	    // models.load_models({
	    //     model: 'stock.warehouse',
	    //     fields: ['id','name'],
	    //     domain: function(self) {
	    //     	return [['id', 'in', self.config.warehouse_ids]];
	    //     },
	    //     loaded: function(self, pos_custom_location)
	    //     {
		   //      self.pos_custom_location = pos_custom_location;
		   //      self.loc_by_id = [];
		   //      pos_custom_location.forEach(function(loc)
		   //      {
		   //          self.loc_by_id[loc.id] = loc;

		   //      });

		   //  },
	   	// });

		const OrderSuper = (Order) => class OrderSuper extends Order {
	    constructor(obj, options) {
			super(...arguments);
	    	this.order_products = this.order_products || {};
				this.prd_qty = this.prd_qty || {};
				this.loaded_qty = this.loaded_qty || {};
		}
				

			set_loaded_qty(qty){
				this.loaded_qty = qty;
				// this.trigger('change',this);
			}

			export_as_JSON() {
				var self = this;
				var loaded = super.export_as_JSON(...arguments);
				loaded.loaded_qty = self.loaded_qty || {};
				loaded.order_products = self.order_products || {};
				 // loaded.prd_qty = self.calculate_prod_qty() || {};
				return loaded;
			}

			init_from_JSON(json){
				super.init_from_JSON(...arguments);
				this.order_products = json.order_products || {};
				this.prd_qty = json.prd_qty || {};
				this.loaded_qty = json.loaded_qty || {};
			}
			get_display_product_qty(prd){
				var self = this;
				var products = {};
				var order = this.pos.get_order();
				var display_qty = 0;
				if(order){
					var orderlines = order.get_orderlines();
					if(orderlines.length > 0 && self.pos.config.default_location_src_id){
						orderlines.forEach(function (line) {
							if(line.product['id'] == prd.id){
								display_qty += line.get_quantity()
							}
						});
					}
				}
				
				return display_qty
			}

			calculate_prod_qty() {
				var self = this;
				var products = {};
				var order = this.pos.get_order();
				if(order){
					var orderlines = order.get_orderlines();
					var config_loc = self.pos.config.default_location_src_id[0];
					if(order.prd_qty  == undefined){
						order.prd_qty = {};
					}
					if(order.order_products  == undefined){
						order.order_products = {};
					}

					if(orderlines.length > 0 && self.pos.config.default_location_src_id){
						orderlines.forEach(function (line) {
							var prod = line.product;

							order.order_products[prod.id] = self.pos.prod_with_quant[prod.id];
							var loc = line.stock_location_name;
							
							if(prod.type == 'product'){
								if(products[loc] == undefined){
									products[loc] =  [{
										'loc' :loc,
										'line' : line.id,
										'name': prod.display_name,
										'id':prod.id,
										'prod_qty' : self.get_display_product_qty(line.product),
										'qty' :parseFloat(line.quantity)
									}];
								}
								else{
									let found = $.grep(products[loc], function(v) {
										return v.id === prod.id;
									});
									if(found){
										products[loc].forEach(function (val) {
											if(val['id'] == prod.id){
												if(val['line'] == line.id){
													val['qty'] = parseFloat(line.quantity);
												}else{
													val['qty'] += parseFloat(line.quantity);
												}
											}
										});
									}
									if(found.length == 0){
										products[loc].push({
											'loc' :loc,
											'line' : line.id,
											'name': prod.display_name,
											'id':prod.id,
											'prod_qty' : self.get_display_product_qty(line.product),
											'qty' :parseFloat(line.quantity)
										})
									}
								}
							}
						});
					}
					order.prd_qty = products;
					
				}

				return products;
			}

			
		}
	Registries.Model.extend(Order, OrderSuper);


	const CustomOrderLine = (Orderline) => class CustomOrderLine extends Orderline{


		constructor(obj, options){
			super(...arguments);
			this.stock_location_id = this.stock_location_id || false;
	        this.stock_location_name = this.stock_location_name || false;
	    }

	    set_stock_location_name(stock_location_name){
	        this.stock_location_name = stock_location_name
	        this.trigger('change',this);
	    }
	    get_stock_location_name(){
	        return this.stock_location_name;
	    }

	    set_stock_location_id(stock_location_id){
	        this.stock_location_id = stock_location_id
	        this.trigger('change',this);
	    }
	    get_stock_location_id(){
	        return this.stock_location_id;
	    }
	    can_be_merged_with(orderline) {
	          if (orderline.get_stock_location_name() !== this.get_stock_location_name()) {
	            return false;
	        } else {
	            return super.can_be_merged_with(...arguments);;
	        }

	    }
	    export_for_printing(){
			var json = super.export_for_printing(...arguments);
			json.is_location_warehouse = this.get_stock_location_name();
			return json;
		}
	    export_as_JSON(){

	        var json = super.export_as_JSON(...arguments);
	        json.stock_location_name = this.get_stock_location_name();
	        return json;
	    }
	    init_from_JSON(json){
	    	super.init_from_JSON(...arguments);
	         // _super_orderline.init_from_JSON.apply(this,arguments);
	        this.stock_location_name = json.stock_location_name;

	    }
	}
	Registries.Model.extend(Orderline, CustomOrderLine);
	
});







