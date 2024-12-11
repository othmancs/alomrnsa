$(document).ready(function() {
    $('.select2').select2({
    closeOnSelect: false
    },);
    $('.select2').on('select2:select', function (e) {
    var data = e.params.data;
    });
});