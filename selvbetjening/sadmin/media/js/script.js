/* Author:

*/
var last_search = null;
var search_url = null;

function init_livesearch(searchUrl) {
    var typeDelay = 200;
    search_url = searchUrl;

    $('#searchbox').keyup(function () {
        if (this.value != this.lastValue) {
            var query = this.value;

            if (this.requestTimer) {
                clearTimeout(this.requestTimer);
            }

            this.requestTimer = setTimeout(function() {
		do_search(query);
            }, typeDelay);

            this.lastValue = query;
        }
    });
};

function do_search(url) {
    last_search = search_url + url;

    jQuery.get(last_search, function(data) {
                    if (data.length) {
                        $('#changelist-form').html(data);
			prepare_changelist();
                    }
                    else {
			last_search = null;
                        $('#changelist-form').html('');
                    }
    });
}

function repeat_search() {
    do_search(last_search);
}

function prepare_changelist() {
    // apply the "success, failure and warning" class tocells containing a span
    // with the equivalent classes. Ugly hack to allow admin generated values to
    // change the display of the parent container

    $("td span.success").parent().addClass("success");
    $("td span.warning").parent().addClass("warning");
    $("td span.error").parent().addClass("error");

	if ($(".iframe").fancybox) {
		$(".iframe").fancybox({
					'width'				: '100%',
					'height'				: '100%',
					'scrolling'				: 'no',
					'autoScale'				: true,
					'transitionIn'			: 'elastic',
					'transitionOut'			: 'elastic',
					'type'				: 'iframe'
				});
	}

}

$(document).ready(prepare_changelist);