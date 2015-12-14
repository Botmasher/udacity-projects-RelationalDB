
// John Resig scroll code - /!\ do NOT attach directly to scroll event listener
// http://ejohn.org/blog/learning-from-twitter/
//var outerPane = $details.find(".details-pane-outer")
var didScroll = false;

$(window).scroll(function() {
	didScroll = true;
});

setInterval(function() {
    if ( didScroll ) {
        didScroll = false;
    	// Check your page position and then
    	// Load in more results
        if ( $(window).scrollTop() >= $("#temporaryDiv").offset().top ) {
			$.ajax({
				url: 'http://en.wikipedia.org/w/api.php?action=opensearch&search=NYC&format=json&callback=wikiCallback/',
				dataType: 'jsonp',
				success: function(json) {
					$('#temporaryDiv').text('We are done here!');
				},
				error: function(e) {
					$('#temporaryDiv').text('<p>'+e+'</p>' + '<p>Failed to load content!</p>');
				}
			});
	    }
	}
}, 250);