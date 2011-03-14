/* Author:

*/

function init_livesearch(searchbox, resultsArea, searchUrl) {
    var typeDelay = 200;
    searchbox.keyup(function () {
        if (this.value != this.lastValue) {
            var query = this.value;

            if (this.requestTimer) {
                clearTimeout(this.requestTimer);
            }

            this.requestTimer = setTimeout(function() {
                jQuery.get(searchUrl + query, function(data) {
                    if (data.length) {
                        resultsArea.html(data);
                    }
                    else {
                        resultsArea.html('');
                    }
                });
            }, typeDelay);

            this.lastValue = query;
        }
    });
};

$(document).ready(function() {
    // apply the "success, failure and warning" class tocells containing a span
    // with the equivalent classes. Ugly hack to allow admin generated values to
    // change the display of the parent container

    $("td span.success").parent().addClass("success");
    $("td span.warning").parent().addClass("warning");
    $("td span.error").parent().addClass("error");

    $(".iframe").fancybox({
				'width'				: '100%',
				'height'			: '100%',
				'scrolling'			: 'no',
				'autoScale'			: true,
				'transitionIn'		: 'elastic',
				'transitionOut'		: 'elastic',
				'type'				: 'iframe'
			});
});