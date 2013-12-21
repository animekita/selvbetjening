
function init_livesearch(search_url) {
    var TYPE_DELAY = 200;

    var current_page = 1;
    var current_request = null;
    var current_more_request = null;

    // call this before creating a new request of other type, this ensures that we only have
    // one active request (that will change the page) at any one time.
    function neutralize_current_environment() {
        if (current_request != null && current_request.abort) {
            current_request.abort();
        }

        if (current_more_request != null && current_more_request.abort) {
            current_more_request.abort();
        }
    }

    $('#searchbox').keyup(function() {
        if (this.value != this.lastValue) {
            var query = this.value;

            if (this.requestTimer) {
                clearTimeout(this.requestTimer);
            }

            this.requestTimer = setTimeout(function() {
			    neutralize_current_environment();

                current_request = jQuery.get(search_url + query, function(data) {

                    current_page = 1;

                    if (data.indexOf('fragment-has-next') != -1) {
                        $('#searchmore').show();
                    } else {
                        $('#searchmore').hide();
                    }

                    $('#searchresult').html(data.length ? data : '');
                });

            }, TYPE_DELAY);

            this.lastValue = query;
        }
    });

    $('#searchmore').click(function(e) {
        e.stopPropagation();
        e.preventDefault();

        neutralize_current_environment();

        var query = $('#searchbox')[0].value;
        var requested_page = current_page + 1;

        current_more_request = jQuery.get(search_url + query + "&page=" + requested_page, function(data) {
            current_page = requested_page;

            if (data.trim() != '') {
                $('#searchresult').append(data);
            }

            if (data.indexOf('fragment-has-next') != -1) {
                console.log(data.contains('fragment-has-next'));
                $('#searchmore').show();
            } else {
                $('#searchmore').hide();
            }

        });
    });
}

window.sinit_livesearch = init_livesearch;

$(document).ready(function(){
    $('textarea').autosize();
});

function popup(url, name, height, width) {
	var newwindow = window.open(url, name, 'height=' + height + ',width=' + width);
	if (window.focus) { newwindow.focus() }

    return false;
}

window.spopup = popup;

