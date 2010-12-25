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




















