
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
		// $.getJSON('/loadMoreResults/', {
		//    	//a: $('input[name="a"]').val(),
		//    	//b: $('input[name="b"]').val()
		//    }, function(data) {
		//    	$("#temporaryDiv").text(data.puppies[0]);
		//    });
			$.ajax({
				url: '/puppies/JSON/',
				dataType: 'json',
				success: function(json) {
					$('#temporaryDiv').text(json);
				},
				error: function(e) {
					$('#temporaryDiv').text('Error! Failed to load content!');
				}
			});
	    }
	}
}, 250);