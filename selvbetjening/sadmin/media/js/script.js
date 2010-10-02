/* Author: 

*/

function init_livesearch(searchbox, resultsArea, searchUrl) {
    var duration = 400;
    var typeDelay = 200;

    // Auto update live-search onkeyup
    searchbox.keyup(function () {
        // Don't update live-search if it's got the same value as last time
        if (this.value != this.lastValue) {
            var q = this.value;

            // Stop previous ajax-request
            if (this.timer) {
                clearTimeout(this.timer);
            }

            // Start a new ajax-request in X ms
            this.timer = setTimeout(function () {
                jQuery.get(searchUrl + q, function (data) {
                    // Show live-search if results and search-term aren't empty
                    if (data.length && q.length) {
                        resultsArea.html(data);
                    }
                    else {
                        resultsArea.html('');
                    }
                });
            }, typeDelay);

            this.lastValue = q;
        }
    });
};




















