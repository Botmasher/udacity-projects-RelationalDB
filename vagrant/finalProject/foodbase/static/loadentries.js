$(function () {
	// bind ajax to link click
	$(".loadentries").click(function(el) {
		// retrieve app-internal serialized data
		$.getJSON("/Restaurant/JSON/", function(data) {

			// prepare array to store json entries while iterating
			var imageList = [];

			// break down clicked url for paginated results
			var urlName = el.target.name;
			// grab the first number in name, used to pass page number
			var pageNumber = parseInt(urlName.split("-")[0]);
			// grab the second number in name, used to pass results per page
			var resultsPerPage = parseInt(urlName.split("-")[1]);

			// calculate first and last db entries to display
			var startIndex = (pageNumber * resultsPerPage) - resultsPerPage + 1;
			var endIndex = pageNumber * resultsPerPage;

			var counter = 0; 	// keep track of how many entries so far

			// iterate through json
			for (var i in data) {
				// iterate through entries
				for (var j in data[i]) {
					
					counter ++;

					// display expected db index results for this page
					if (counter >= startIndex && counter <= endIndex) {
						// use keys to display image and build link
						imageList.push("<div class='oneimg'><a href='/restaurants/" + data[i][j]["id"] + "/menu/'><h3>" + data[i][j]["name"].substring(0,16) + "...</h3><img src='" + data[i][j]["image"] + "'></a><br><a href='/update/Restaurant/" + data[i][j]["id"] + "/'>edit</a> &nbsp;&nbsp; <a href='/delete/Restaurant/" + data[i][j]["id"] + "/'>delete</a></div>");
					}
				}
			}

			// use array to build replacement image grid
			var imgGrid = $("<div/>",{"class":"frontimgs", html:imageList.join("")});
			// replace current image grid with this image grid
			$("div.frontimgs").replaceWith(imgGrid);
		});
		// stop click from loading URL
		return false;
	});
});