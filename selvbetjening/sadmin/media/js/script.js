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

$(function(){
    // apply the "success, failure and warning" class tocells containing a span
    // with the equivalent classes. Ugly hack to allow admin generated values to
    // change the display of the parent container

    $("td span.success").parent().addClass("success");
    $("td span.warning").parent().addClass("warning");
    $("td span.error").parent().addClass("error");
});