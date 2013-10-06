var selvbetjening = new Object();

$(function() {

    function update_checkbox_class(checkbox) {

        if (checkbox.checked) {
            $(checkbox.parentNode).addClass('checkbox_checked');
        } else {
            $(checkbox.parentNode).removeClass('checkbox_checked');
        }

    }
    selvbetjening.update_checkbox_class = update_checkbox_class;

    $('.checkboxinput').live('change', function() {update_checkbox_class(this);});
    $('.checkboxinput').each(function(i, input) {update_checkbox_class(input);});

});