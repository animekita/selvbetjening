
function init_livesearch(search_url) {
    var TYPE_DELAY = 200;

    var current_request = null;

    $('#searchbox').keyup(function () {
        if (this.value != this.lastValue) {
            var query = this.value;

            if (this.requestTimer) {
                clearTimeout(this.requestTimer);
            }

            this.requestTimer = setTimeout(function() {
			    if (current_request != null && current_request.abort) {
				    current_request.abort();
				}

                current_request = jQuery.get(search_url + query, function(data) {
                    $('#searchresult').html(data.length ? data : 'kk');
                });

            }, TYPE_DELAY);

            this.lastValue = query;
        }
    });
}
