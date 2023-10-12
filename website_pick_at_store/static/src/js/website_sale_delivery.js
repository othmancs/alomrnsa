/** @odoo-module **/


import "website_sale_delivery.checkout";
import publicWidget from "web.public.widget";
import {DropPrevious} from "web.concurrency";
import {qweb as QWeb, _t} from "web.core";



const WebsiteSaleDeliveryWidget = publicWidget.registry.websiteSaleDelivery;

WebsiteSaleDeliveryWidget.include({
    init: function() {
        this.dp = new DropPrevious();
        this._super.apply(this, arguments);
    },
    _handleCarrierUpdateResult: function (result) {
        this.warehouses = [];
        var self = this;
        this._super.apply(this, arguments);
        if($('#store-list-pickup').length > 0){
            $('#store-list-pickup').remove();
        }
        if($('#store-list-btn').length > 0){
            $('#store-list-btn').remove();
        }
        if(result.personal_store_pickup){
            if(result.warehouses.length > 0){
                this.warehouses = result.warehouses;
                let $storeContainer = $(QWeb.render('website_pick_at_store.Container', {
                    uniqueId: 'store-list-btn',
                    productFrame: 1,
                    store: result.warehouse,
                }));
                var $last = $('.o_delivery_carrier_select').last();
                $last.after($storeContainer);
                this._renderStoreListDetail(this.warehouses);
                $('#delivery_method .btn-click button').on('click', self._onToggleStoreSearchList.bind(self));
                $('#delivery_method .box-search input').on('keyup', self._onInputSearchStore.bind(self));
                $('#store-list-pickup').on('focusout', self._onBlurStoreBox.bind(self));
                _.each(this.warehouses, function(wh){
                    if (wh.id === result.warehouse_id){
                        self._toggleStoreSearchList();
                        return;
                    }
                });
            }
            else{
                alert(_t('It is not possible to pick-up this order in our stores'));
                $('.o_delivery_carrier_select').first().click();
            }

            if($('.delivery_note').length){
                $('.delivery_note').remove();
            }

            if($('.delivery_messege').length){
                $('.delivery_messege').remove();
            }
        }
    },

    _onToggleStoreSearchList: function(ev){
        // var $btn = $(ev.currentTarget);
        this._toggleStoreSearchList();
    },
    _toggleStoreSearchList: function(){
        var $StoreList = $('#store-list-pickup');
        var $btn = $('#store-list-btn button');
        $btn.toggleClass('active');
        $StoreList.toggleClass('active');
        if ($StoreList.hasClass('active')){
            $StoreList.find('.box-search input').focus();
            //$StoreList.focusin();
        }
        else {
            //$StoreList.focusout();
        }
    },
    _onInputSearchStore: function(ev){
        var self = this;
        var $input = $(ev.currentTarget);
        var searchKeyWord = $input.val();
        var stores = [];
        if ((!searchKeyWord || searchKeyWord == '') && this.warehouses){
            stores = this.warehouses;
        }
        else if (this.warehouses){
            _.each(this.warehouses, function(wh){
                if (wh.name && self._makeUpKeyWord(wh.name).search(searchKeyWord) != -1){
                    stores.push(wh);
                }
                else if (wh.address && self._makeUpKeyWord(wh.address).search(searchKeyWord) != -1){
                    stores.push(wh);
                }
            });
        }
        this._renderStoreListDetail(stores);
        
    },
    _renderStoreListDetail: function(stores, productFrame=1){
        let $container = $('#delivery_method div.select div.store-list');
        let $StoreListDetail = $(QWeb.render('website_pick_at_store.StoreListDetail', {
            productFrame: productFrame,
            stores: stores,
        }));
        $container.replaceWith($StoreListDetail);
        $('#store-list-pickup button.store-item ').on('click', this._onClickPickupAddress.bind(this));
    },
    _onClickPickupAddress: function(ev){
        var warehouseId = $(ev.currentTarget).data('warehouseId');
        var warehouseName = $(ev.currentTarget).data('warehouseName');
        if (warehouseId && warehouseName){
            $('#store-list-btn button').html(warehouseName);
            $('#store-list-btn input').val(warehouseId);
            this._deactivateStoreBox();
            this.dp.add(this._rpc({
                route: '/shop/update_pickup_warehouse',
                params: {
                    warehouse_id: warehouseId,
                },
            }));
        }
    },
    _onBlurStoreBox: function(ev){
        if (!ev.relatedTarget){
            //this._deactivateStoreBox();
        }
    },
    _deactivateStoreBox: function(){
        $('#store-list-pickup').removeClass('active');
        $('#store-list-btn button').removeClass('active');
    },

    _makeUpKeyWord: function(keyWord){
        return keyWord.toLowerCase();
    },
});
    