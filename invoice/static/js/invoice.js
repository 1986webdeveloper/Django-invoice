function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}
function cloneMore(selector, prefix) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();

    newElement.find(':input:not([type=button]):not([type=submit]):not([type=reset])').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-', '-' + total + '-')
        $(this).attr({'name': name, 'id': 'id_' + name}).val('');
    });
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
    return false;
}

function deleteForm(prefix, btn) {
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total > 1){
        btn.closest('.test').remove();
        var forms = $('.test');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for (var i=0, formCount=forms.length; i<formCount; i++) {
            $(forms.get(i)).find(':input').each(function() {
                updateElementIndex(this, prefix, i);
            });
        }
    }
    invoice_calculation()
    return false;
}
$(document).on('click', '.add-form-row', function(e){
	console.log("yes cl")
    e.preventDefault();
    cloneMore('.test:last', 'invoiceline_set');
    return false;
});

$(document).on('click', '.cut', function(e){
    e.preventDefault();
    deleteForm('invoiceline_set', $(this));
    return false;
});

$("#invoice_table").on("change", "input", function() {
	var row = $(this).closest("tr")
	var qty = parseFloat(row.find("input[name='invoiceline_set-"+row.index()+"-quantity']").val());
	var price = parseFloat(row.find("input[name='invoiceline_set-"+row.index()+"-price'] ").val());
	var total = (isNaN(qty) ? 0: qty) * (isNaN(price) ? 0: price);
	row.find("input[name='invoiceline_set-"+row.index()+"-line_total']").val(isNaN(total) ? "" : total);
	invoice_calculation()
});

function invoice_calculation(){
	var subtotal = parseFloat(0.000)
    $('#invoice_table > tbody  > tr').each(function() {
    	subtotal += parseFloat($(this).find("input[name='invoiceline_set-"+$(this).index()+"-line_total']").val())
    });
    $('#id_subtotal').val(subtotal)
    $('#id_total').val(subtotal)

    var discount = isNaN(parseFloat($('#id_discout').val())) ? parseFloat(0.000) : $('#id_discout').val()
    var tax = isNaN(parseFloat($('#id_tax').val())) ? parseFloat(0.000) : $('#id_tax').val()
    var shipping_charge = isNaN(parseFloat($('#id_shipping_charge').val())) ? parseFloat(0.000) : $('#id_shipping_charge').val()
    var amount_paid = isNaN(parseFloat($('#id_amount_paid').val())) ? parseFloat(0.000) : $('#id_amount_paid').val()
    var discounted_price = subtotal - (subtotal * (discount/parseFloat("100")))
    var text_included_price = discounted_price  + (discounted_price * (tax/parseFloat("100")))
    var shipping_charge_included_price = text_included_price + parseFloat(shipping_charge)
    $('#id_total').val(shipping_charge_included_price)
    var balance_due = (shipping_charge_included_price - amount_paid).toFixed(2)
    $('#id_balance_due').val(balance_due)

}

$("#id_tax,#id_amount_paid,#id_discout,#id_shipping_charge").on("change",function(){
	invoice_calculation()
})

function showImage(src, target) {
    var fr = new FileReader();
    fr.onload = function(){
     	target.src = fr.result;
    }
   	fr.readAsDataURL(src.files[0]);

 }
function putImage() {
    var src = document.getElementById("select_image");
    var target = document.getElementById("target");
    showImage(src, target);
}