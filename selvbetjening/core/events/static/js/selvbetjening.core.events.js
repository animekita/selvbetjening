$(function() {

    /*
     * Package support
     */

    // select or deselect all items if package is selected or deselected
    $('.package').live('change', function() {

        var items = $(this).parent().siblings('.in_' + this.name).children('input');

        for (i = 0; i < items.length; i++) {
            items[i].checked = this.checked;
            $(items[i]).trigger('change');
        }

    });

    // deselect package if item is deselected
    $('input.in_package').live('change', function() {

        if (this.checked == false) {
            var p = $(this).parent().prevAll('div.package').children('input');

            if (p.length > 0 && p[0].checked) {
                p[0].checked = false;
                selvbetjening.update_checkbox_class(p[0]);
            }
        }
    });

    // set the package to selected on load if all items are selected
    $('div.package').each(function(i, p) {
        var input = $(p).siblings('div.in_package').children('input');

        for (i = 0; i < input.length; i++) {
            if (input[i].checked == false) return;
        }

        $(p).children('input').each(function(i, input) {
            input.checked = true;
            selvbetjening.update_checkbox_class(input);
        });
    });

});