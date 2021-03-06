$(function() {

    /*
     * Package support
     */

    // select or deselect all items if package is selected or deselected
    $('.package').delegate('change', function() {

        var items = $('.in_' + this.name);

        for (var i = 0; i < items.length; i++) {
            items[i].checked = this.checked;
            $(items[i]).trigger('change');
        }

    });

    // deselect package if item is deselected
    $('input.in_package').delegate('change', function() {

        if (this.checked == true) {
            return;
        }

        var inRegex = /^in_package_([0-9]+)$/;
        var classes = $(this)[0].className.split(/\s+/);

        for (var i = 0; i < classes.length; i++) {
            var match = classes[i].match(inRegex);

            if (match != null) {
                var package_input = $('#id_package_' + match[1]);

                if (package_input.length > 0 && package_input[0].checked) {
                    package_input[0].checked = false;
                    selvbetjening.update_checkbox_class(package_input[0]);
                }

            }
        }
    });

    // set the package to selected on load if all items are selected
    $('input.package').each(function(i, p) {

        var idRegex = /^id_package_([0-9]+)$/;
        var id = p.id.match(idRegex)[1];

        var input = $('.in_package_' + id);

        for (j = 0; j < input.length; j++) {
            if (input[j].checked == false) return;
        }

        $(p)[0].checked = true;
        selvbetjening.update_checkbox_class($(p)[0]);
    });

    $("[data-depends-on]").each(function(i, p) {

        var node = $(p);
        var dependency = $("[name=" + p.getAttribute('data-depends-on') + "]");

        var parentBlock = node.parents('.form-group');
        var nodeIsRequired = node.attr('required') != undefined;

        function update(fast) {
            if (dependency.prop('checked')) {

                parentBlock.fadeIn();

                if (nodeIsRequired) {
                    node.attr('required', 'required');
                }
            } else {
                parentBlock.fadeOut();
                node.removeAttr('required');
            }
        }

        update(true);

        dependency.change(update);
    });
});

