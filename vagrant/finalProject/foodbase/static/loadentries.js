$(function () {
	// bind ajax to link click
	$('a#testAjax').bind('click', function() {
		// retrieve app-internal serialized data
		$.getJSON("/Restaurant/JSON/", function(data) {
			
			// prepare array to store data entries
			var listItems = [];

			// iterate through json
			for (var i in data) {
				// iterate through entries
				for (var j in data[i]) {
					// iterate through values for individual entry
					for (var k in data [i][j]) {
						// log entries
						listItems.push("<li id=''>" + data[i][j][k] + "</li>");
					}
				}
			}

			// use array to build html list
			$("<ul/>",{"class":"my-new-list", html:listItems.join("")}).appendTo("#print_ajax_here");
		});
		// stop click from loading URL
		return false;
	});
});