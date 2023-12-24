odoo.define('signup_with_phone.country_code', function(require) {
    'use strict';

    var core = require('web.core');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var select_val;
    var codenumber;

    $(document).ready(function(){
        if($("#signup_field_set").val() =='true') {
            var input = document.querySelector("#phone");
            var errorMsg = document.querySelector("#error-msg");
            var validMsg = document.querySelector("#valid-msg");

            // here, the index maps to the error code returned from getValidationError - see readme
            var errorMap = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];

            var reset = function() {
                input.classList.remove("error");
                errorMsg.innerHTML = "";
                errorMsg.classList.add("o_hidden");
                validMsg.classList.add("o_hidden");
            };

            var iti = window.intlTelInput(input, {
                initialCountry: "auto",
                autoPlaceholder: "aggressive",
                separateDialCode: true,
                geoIpLookup: function(success, failure) {
                    $.get("http://ip-api.com/json/?fields=status,countryCode", function() {}, "jsonp").always(function(resp) {
                        var countryCode = (resp && resp.countryCode) ? resp.countryCode : "us";
                        success(countryCode);
                    });
                },
                customPlaceholder: function(selectedCountryPlaceholder, selectedCountryData) {
                    return selectedCountryPlaceholder;
                },
            });

            var countryData = iti.getSelectedCountryData();
            select_val = countryData['dialCode']
            $("#countrycode").val(select_val);

            var checkMobileNumber = function() {
                reset();
                if (input.value.trim()) {
                    if (iti.isValidNumber()) {
                        $(".btn-primary").removeClass("button disabled");
                        $(".btn-primary").removeAttr('disabled', 'disabled');
                        validMsg.classList.remove("o_hidden");
                        codenumber = $("#phone").val();
                        var symbol = '+'
                        var res = symbol.concat(select_val,codenumber);
                        var phone_number = $("#mobile").val(res);
                        $("#login").val(res);
                    } else {
                        $(".btn-primary").attr('disabled', 'disabled');
                        $(".btn-primary").addClass("button disabled");
                        input.classList.add("error");
                        var errorCode = iti.getValidationError();
                        errorMsg.innerHTML = errorMap[errorCode];
                        errorMsg.classList.remove("o_hidden");
                    };
                };
            };

            input.addEventListener("countrychange", function() {
                var countryData = iti.getSelectedCountryData();
                select_val = countryData['dialCode']
                $("#countrycode").val(select_val);
                checkMobileNumber();
            });

            if($("#phone")) {
                $(".btn-primary").attr('disabled', 'disabled');
                $(".btn-primary").addClass("button disabled");
                $(".field-login").addClass('o_hidden');
            };

            // on keyup: validate and check mobile number
            input.addEventListener('keyup', checkMobileNumber);
            // on change flag: reset
            input.addEventListener('change', reset);
        };

        if($("#signin_field_set").val() =='true') {
            var input = document.querySelector("#mobile");
            var errorMsg = document.querySelector("#error-msg");
            var validMsg = document.querySelector("#valid-msg");

            var iti = window.intlTelInput(input, {
                initialCountry: "auto",
                autoPlaceholder: "aggressive",
                separateDialCode: true,
                geoIpLookup: function(success, failure) {
                    $.get("http://ip-api.com/json/?fields=status,countryCode", function() {}, "jsonp").always(function(resp) {
                        var countryCode = (resp && resp.countryCode) ? resp.countryCode : "us";
                        success(countryCode);
                    });
                },
                customPlaceholder: function(selectedCountryPlaceholder, selectedCountryData) {
                    return selectedCountryPlaceholder;
                },
            });

            // here, the index maps to the error code returned from getValidationError - see readme
            var errorMap = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];
            var reset = function() {
                input.classList.remove("error");
                errorMsg.innerHTML = "";
                errorMsg.classList.add("o_hidden");
                validMsg.classList.add("o_hidden");
            };

            var countryData = iti.getSelectedCountryData();
            select_val = countryData['dialCode']
            $("#countrycode").val(select_val);

            var checkMobileNumber = function() {
                reset();
                if (input.value.trim()) {
                    if (iti.isValidNumber()) {
                        $(".btn-primary").removeClass("button disabled");
                        $(".btn-primary").removeAttr('disabled', 'disabled');
                        validMsg.classList.remove("o_hidden");
                        codenumber = $("#mobile").val();
                        var symbol = '+'
                        var res = symbol.concat(select_val,codenumber);
                        var mobile_number = $("#numbercode").val(res);
                        $("#login").val(res);
                    } else {
                        $(".btn-primary").attr('disabled', 'disabled');
                        $(".btn-primary").addClass("button disabled");
                        input.classList.add("error");
                        var errorCode = iti.getValidationError();
                        errorMsg.innerHTML = errorMap[errorCode];
                        errorMsg.classList.remove("o_hidden");
                    };
                };
            };

            input.addEventListener("countrychange", function() {
                // do something with iti.getSelectedCountryData()
                var countryData = iti.getSelectedCountryData();
                select_val = countryData['dialCode']
                $("#countrycode").val(select_val);
                checkMobileNumber();
            });

            if($("#mobile")){
                $(".btn-primary").attr('disabled', 'disabled');
                $(".btn-primary").addClass("button disabled");
                $(".field-login").addClass('o_hidden');
            };

            // on keyup: validate and check mobile number
            input.addEventListener('keyup', checkMobileNumber);
            // change flag: reset
            input.addEventListener('change', reset);
        };
    });
});
