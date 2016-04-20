$(function () {
	// bind ajax to link click
	$("a#testAjax").bind("click", function() {
		// retrieve app-internal serialized data
		$.getJSON("/Restaurant/JSON/", function(data) {
			
			// prepare array to store json entries while iterating
			var listItems = [];

			// break down url for paginated results
			var urlName = $("a#testAjax").attr("name");
			// grab the first number in url, used to pass page number
			var pageNumber = parseInt(urlName.split("-")[0]);
			// grab the second number in url, used to pass results per page
			var resultsPerPage = parseInt(urlName.split("-")[1]);

			// calculate first and last db entries to display
			var startIndex = ((pageNumber-1) * resultsPerPage) + 1;
			var endIndex = pageNumber * resultsPerPage;

			var counter = 0;

			// iterate through json
			for (var i in data) {
				// iterate through entries
				for (var j in data[i]) {
					counter ++;
					// display expected db index results for this page
					if (counter >= startIndex && counter <= endIndex) {
						// use keys to display image and build link
						listItems.push("<div class='oneimg'><a href='/restaurants/" + data[i][j]["id"] + "/menu/'><img src='" + data[i][j]["image"] + "'></a></div>");
					}
				}
			}

			// use array to build html image grid
			$("<div/>",{"class":"frontimgs", html:listItems.join("")}).appendTo("#print_ajax_here");
		});
		// stop click from loading URL
		return false;
	});
});