odoo.define("payment_attachment.payment_attachment", function (require) {
    "use strict";
    var publicWidget = require("web.public.widget");

  
    publicWidget.registry.PaymentAttachment = publicWidget.Widget.extend({
      selector: "#wrapwrap",
      events: {
        "click .submit_proof": "_submitForm",
        "change #txn_proof":"_toggleUpload",
        "click .toggle_upload": "_submitConfirmForm",
        "click #preview_reciept":"_showPreview",
      },

      _submitConfirmForm: function(ev){
        $(ev.currentTarget).closest(".txn_receipt_block").find("form").submit();
      },
      _showPreview:function(ev){
        ev.preventDefault();
        var image = $("#preview_reciept+div.image_url img").attr("src");
        window.location.href = image;
      },
  
      _submitForm:function(ev){
        $(ev.currentTarget).closest(".modal-content").find("form").submit();
      },

      _toggleUpload:function(ev){
        var attachment = $(ev.currentTarget).val();
        console.log(attachment);
        if(attachment){
          $(".toggle_upload").prop("disabled",false);
        }
        else{
          $(".toggle_upload").prop("disabled",true);
        }
      },
    });
  });
  