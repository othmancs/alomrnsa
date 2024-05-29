odoo.define('portal_sale_order.portal_form', function(require){
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    // var core = require('web.core');

    const select4Options = {
        theme: 'bootstrap',
        minimumResultsForSearch: 1,
        width: 'resolve'
    }



    publicWidget.registry.portalApprovalRequest = publicWidget.Widget.extend({
        selector: '.o_portal_approval',
        events: {
            'click #add_child_row': '_onAddChild',
            'click .delete-row': '_onDeleteRow',
            'click #hidden_box_btn': '_onModalShow',
            'change .product_select': '_onProductSelectChange',
            'change .pricelist_line_id': '_onProductSelectChange',
            'change #partner_id': '_onChangePartnerId',
            'click #submit_customer': '_onClickSubmitCustomer',
            'submit': '_onFormSubmit'
        },

        start: function () {
            var def = this._super.apply(this, arguments);

            this.$childRowTemplate = $('#child_row_template');
            this.$childTableBody = $('#child_table_body');
            this.$partner = $('#partner_id')
            this.$pricelist = $('#pricelist_id')
            this.$branch = $('#branch_id')

            this.$partner.select4({...select4Options, placeholder:'Select Customer'})
            this.$pricelist.select4({...select4Options, placeholder:'Select Pricelist'})
            this.$branch.select4({...select4Options, placeholder:'Select Branch'})


            this.$childTableBody.find('tr').each(function() {
                // Skip the template row
                if ($(this).css('display') === 'none') {
                    return true;
                }
                $(this).find('select[name="select_product"]').select4({...select4Options, placeholder:'Select Product'});
                $(this).find('select[name="select_warehouse"]').select4({...select4Options, placeholder:'Select Warehouse'});
                $(this).find('select[name="pricelist_line_id"]').select4({...select4Options, placeholder:'Select PriceList'});
            });


            return def;
        },
        _onChangePartnerId: function (event){
            var self = this;
            var selected_partner = $(event.currentTarget);
            this.$pricelist.val(selected_partner.find('option:selected').data('pricelist')).change()
        },

        _onAddChild: function () {
            // Check if there is more than one row in the table (first row is always empty)
            if (this.$childTableBody.find('tr:visible').length >= 1) {
                var lastRowProductSelect = this.$childTableBody.find('tr:last .product_select');
                if (lastRowProductSelect.val() === "") {
                    alert("Please select a product in the last row before adding a new one.");
                    return;
                }
            }
            if (this.$pricelist.val() === ""){
                alert("Please select Pricelist to add products.")
                return;
            }

            var newRow = $(this.$childRowTemplate[0].cloneNode(true));
            newRow.show();
            // Clear all the fields
            newRow.find('select[name="select_product"]')
                .prop('selectedIndex', 0)
                .select4({...select4Options, placeholder:'Select Product'});
            newRow.find('select[name="select_warehouse"]')
                .prop('selectedIndex', 0)
                .select4({...select4Options, placeholder:'Select Warehouse'});
            newRow.find('select[name="pricelist_line_id"]')
                .prop('selectedIndex', 0)
                .select4({...select4Options, placeholder:'Select Pricelist'});

            this.$childTableBody.append(newRow);
        },

        _onDeleteRow: function (event) {
            var row = $(event.target).closest('tr');
            row.remove();
        },

        _onModalShow: function (event) {
            $("#hidden_box").modal('show');
        },

        _onProductSelectChange: function (event) {
            var self = this;
            var eventTarget = $(event.currentTarget);
            var quantity = eventTarget.closest('tr').find('input[name="child_quantity[]"]').val();
            var price = eventTarget.closest('tr').find('input[name="child_price[]"]');
            var ref = eventTarget.closest('tr').find('input[name="child_ref[]"]');
            var uom = eventTarget.closest('tr').find('input[name="child_uom[]"]');
            var productId = eventTarget.closest('tr').find('select[name="select_product"]').val();
            var priceList = this.$pricelist.val()
            if (eventTarget.attr('name') === 'pricelist_line_id'){
                priceList = eventTarget.val();
            } else {
                // Set Ref. and Uom
                ref.val(eventTarget.find('option:selected').data('internal_ref'));
                uom.val(eventTarget.find('option:selected').data('uom'));
                eventTarget.closest('tr').find('select[name="pricelist_line_id"]').val(this.$pricelist.val()).change()
            }

            rpc.query({
                        model: 'product.pricelist',
                        method: 'get_product_price_rpc',
                        args: [parseInt(productId), parseInt(quantity), parseInt(priceList)],
                    }).then(function (priceData) {
                        price.val(parseInt(priceData));
                    });
        },

        _onPricelistLineChange: function (event) {
            var self = this;
            var price_list = $(event.currentTarget);
            var quantity = price_list.closest('tr').find('input[name="child_quantity[]"]').val();
            var productId = price_list.closest('tr').find('select[name="select_product"]').val();
            var price = price_list.closest('tr').find('input[name="child_price[]"]');
            var priceList = price_list.val();

            rpc.query({
                        model: 'product.pricelist',
                        method: 'get_product_price_rpc',
                        args: [parseInt(productId), parseInt(quantity), parseInt(priceList)],
                    }).then(function (priceData) {
                        price.val(parseFloat(priceData));
                    });
        },

        // _onProductSelectChange: function (event) {
        //     var self = this;
        //     var select_product = $(event.currentTarget);
        //     var description = select_product.closest('tr').find('input[name="child_Description[]"]');
        //     var select_uom = select_product.closest('tr').find('select[name="select_uom"]');
        //     var productId = select_product.val();
        //     rpc.query({
        //         model: 'product.product',
        //         method: 'search_read',
        //         args: [[['id', '=', productId]], ['display_name', 'uom_id']],
        //     }).then(function (productData) {
        //         if (productData.length > 0) {
        //             var product = productData[0];
        //             description.val(product.display_name);
        //             // Fetch uom data
        //             rpc.query({
        //                 model: 'uom.uom',
        //                 method: 'search_read',
        //                 args: [[['category_id', '=', product.uom_id[0]]], ['id', 'name']],
        //             }).then(function (uomData) {
        //                 // Clear the uom select element
        //                 select_uom.empty();
        //                 // Add new option elements for each uom
        //                 $.each(uomData, function(i, uom) {
        //                     select_uom.append($('<option></option>').val(uom.id).text(uom.name));
        //                 });
        //             });
        //         }
        //     });
        // },

        _onFormSubmit: function (e) {
            e.preventDefault();

            var lineItems = [];

            this.$childTableBody.find('tr').each(function() {
                // Skip the template row
                if ($(this).css('display') === 'none') {
                    return true;
                }

                var product_id = $(this).find('select[name="select_product"]').val();
                var ref = $(this).find('input[name="child_ref[]"]').val();
                var warehouse_id = $(this).find('select[name="select_warehouse"]').val();
                var unit_price = $(this).find('input[name="child_price[]"]').val();
                var quantity = $(this).find('input[name="child_quantity[]"]').val();
                var uom = $(this).find('input[name="child_uom[]"]').val();

                var item = {
                    product_id: product_id,
                    ref: ref,
                    warehouse_id: warehouse_id,
                    price_unit: unit_price,
                    quantity: quantity,
                    uom: uom
                };
                lineItems.push(item);
            });

            $('input[name="line_items"]').val(JSON.stringify(lineItems));

            this.el.submit();
        },

        _onClickSubmitCustomer: async function (event) {
            event.preventDefault();

            try {
                // Retrieve the values from input fields
                var customer = $('#new_customer').val();
                var phone = $('#new_phone').val();

                // First RPC call to create the customer
                // const customerId = await rpc.query({
                //     model: 'res.partner',
                //     method: 'create',
                //     args: [{
                //         'name': customer,
                //         'phone': phone
                //     }],
                // });
                const customerId = await rpc.query({
                    model: 'res.partner',
                    method: 'create_partner_with_sudo',
                    args: [{
                        'name': customer,
                        'phone': phone
                    }],
                });


                // Second RPC call to fetch the customer data using the created customerId
                const customerData = await rpc.query({
                    model: 'res.partner',
                    method: 'search_read',
                    kwargs: {
                        domain: [
                            ['id', '=', customerId]
                        ],
                        fields: ['id', 'name', 'property_product_pricelist'],
                        limit: 1,
                    }
                });

                if (customerData.length > 0) {
                    const customer = customerData[0];

                    // Create a new option element
                    const option = document.createElement('option');
                    option.value = customer.id;
                    option.setAttribute('data-pricelist', customer.pricelist_id ? customer.pricelist_id[0] : '');
                    option.textContent = customer.name;

                    const selectElement = document.getElementById('partner_id');
                    selectElement.appendChild(option);

                    // Set the newly added option as selected
                    selectElement.value = customer.id;
                }
                $('#new_customer').val('');
                $('#new_phone').val('');
                $("#hidden_box").modal('hide');

            } catch (error) {
                console.error('An error occurred:', error);
            }
        }
    });
});
