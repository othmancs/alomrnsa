odoo.define('payment_telr.payment_form', require => {
    'use strict';

    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');

    const paymentTelrMixin = {

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
		
		
		/**
         * Simulate a feedback from a payment provider and redirect the customer to the status page.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} code - The code of the provider
         * @param {number} providerId - The id of the provider handling the transaction
         * @param {object} processingValues - The processing values of the transaction
         * @return {Promise}
         */
        _processDirectPayment: function (code, providerId, processingValues) {
            if (code !== 'telr') {
                return this._super(...arguments);
            }

            const telr_payment_token = document.getElementById('telr_payment_token').value;
            return this._rpc({
                route: '/payment/telr/process_payment',
                params: {
                    'processing_values': processingValues,
                    'telr_payment_token': telr_payment_token,
                },
            }).then(data => {
				$('#inlineFrame').empty();
                const iframe = '<iframe marginheight="0" marginwidth="0" id="terliframe" frameborder = "0" width="100%" height="450" src="'+data+'" sandbox="allow-forms allow-modals allow-popups-to-escape-sandbox allow-popups allow-scripts allow-top-navigation allow-same-origin"/>';			
				$('#inlineFrame').append(iframe);
				$.unblockUI();
            });
        },

		/**
         * Simulate a feedback from a payment provider and redirect the customer to the status page.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} code - The code of the provider
         * @param {number} providerId - The id of the provider handling the transaction
         * @param {object} processingValues - The processing values of the transaction
         * @return {Promise}
         */
        
		_processRedirectPayment: (code,providerId,processingValues)=>{
			
            if (code !== 'telr') {
                return this._super(...arguments);
            }
			
			const flowtype = processingValues.ivp_framed
			if(flowtype == 2){
				const iframe = '<iframe marginheight="0" marginwidth="0" id="terliframe" frameborder = "0" width="100%" height="450" src="'+processingValues.api_url+'" sandbox="allow-forms allow-modals allow-popups-to-escape-sandbox allow-popups allow-scripts allow-top-navigation allow-same-origin"/>';			
				$('#inlineFrame').append(iframe);
				const $submitButton = this.$('button[name="o_payment_submit_button"]');
				$submitButton.css('display', 'none');
				$.unblockUI();
			}else{
				const $redirectForm = $(processingValues.redirect_form_html).attr('id', 'o_payment_redirect_form');
				$redirectForm[0].setAttribute('target', '_top');
				$(document.getElementsByTagName('body')[0]).append($redirectForm);
				$redirectForm.submit();
			}				
        },
		
		
		/**
         * Prepare the inline form of Demo for direct payment.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} code - The code of the selected payment option's provider
         * @param {integer} paymentOptionId - The id of the selected payment option
         * @param {string} flow - The online payment flow of the selected payment option
         * @return {Promise}
         */
		_prepareInlineForm: function (code, paymentOptionId, flow) {
            if (code !== 'telr') {
                return this._super(...arguments);
            } 
			
			$('#inlineFrame').empty();
			
			return this._rpc({
                route: '/payment/telr/getinfo',
				params: {
                    'provider_id': paymentOptionId,
					'currency_id': this.txContext.currencyId,
					'partner_id':this.txContext.partnerId,
                },
            }).then(data => {
				
				if(data.telr_payment_mode == 10){
					
					this._setPaymentFlow('direct');
					
					var store_id = data.store_id;
					var currency = data.currency_name;
					var test_mode = data.test_mode;
					var saved_cards = data.saved_cards;
					var frameHeight = data.frame_height;
					var language = data.language;
					window.telrInit = false;
					
					
					var telrMessage = {
						"message_id": "init_telr_config",
						"store_id": store_id,
						"currency": currency,
						"test_mode": test_mode,
						"saved_cards": saved_cards
					}
					
					var iframeUrl = "https://secure.telr.com/jssdk/v2/token_frame.html?token=" + Math.floor((Math.random() * 9999999999) + 1) + "&lang=" + language;
					var iframeHtml = ' <iframe id="telr_iframe" src= "' + iframeUrl + '" style="width: 100%; height: '+frameHeight+'px; border: 0;" sandbox="allow-forms allow-modals allow-popups-to-escape-sandbox allow-popups allow-scripts allow-top-navigation allow-same-origin"></iframe>';
					iframeHtml +=  '<input id="telr_payment_token" type="hidden" name="telr_payment_token"/>';
					$('#inlineFrame').append(iframeHtml);

					if (typeof window.addEventListener != 'undefined') {
						window.addEventListener('message', function(e) {
							var message = e.data;
							 if(message != ""){
								var isJson = true;
								try {
									JSON.parse(str);
								} catch (e) {
									isJson = false;
								}
								if(isJson || (typeof message === 'object' && message !== null)){
									var telrMessage = (typeof message === 'object') ? message : JSON.parse(message);
									if(telrMessage.message_id != undefined){
										switch(telrMessage.message_id){
											case "return_telr_token": 
												var payment_token = telrMessage.payment_token;
												console.log("Telr Token Received: " + payment_token);
												$("#telr_payment_token").val(payment_token);
											break;
										}
									}
								}
							}
							
						}, false);
						
					} else if (typeof window.attachEvent != 'undefined') { // this part is for IE8
						window.attachEvent('onmessage', function(e) {
							var message = e.data;
							 if(message != ""){
								 try {
									JSON.parse(str);
								} catch (e) {
									isJson = false;
								}
								if(isJson || (typeof message === 'object' && message !== null)){
									var telrMessage = (typeof message === 'object') ? message : JSON.parse(message);
									if(telrMessage.message_id != undefined){
										switch(telrMessage.message_id){
											case "return_telr_token": 
												var payment_token = telrMessage.payment_token;
												console.log("Telr Token Received: " + payment_token);
												$("#telr_payment_token").val(payment_token);
											break;
										}
									}
								}
							}
							
						});
					}

					jQuery(document).ready(function(){
						$('#telr_iframe').on('load', function(){
							var initMessage = JSON.stringify(telrMessage);
							setTimeout(function(){
								if(!window.telrInit){
									document.getElementById('telr_iframe').contentWindow.postMessage(initMessage,"*");
									window.telrInit = true;
								}
							}, 1500);
						});
					});
				}
				
            });
        },
		
		
		_enableButton: function () {
            if (this._isButtonReady()) {
                const $submitButton = this.$('button[name="o_payment_submit_button"]');
                const iconClass = $submitButton.data('icon-class');
                $submitButton.attr('disabled', false);
				$submitButton.css('display', 'block');
                $submitButton.find('i').addClass(iconClass);
                $submitButton.find('span.o_loader').remove();
                return true;
            }
            return false;
        },
		 
    };
    checkoutForm.include(paymentTelrMixin);
    manageForm.include(paymentTelrMixin);
});
