$(function () {
	// listen for clicks on market link
	$(".market-link").on ("click", function() {
		// build form element to be submitted to change market
		var form = "<div class='select-market'>"
						+ "<form action='/' method='POST'>"
							+ "<input type='text' name='market-name'>"
							+ "<input type='submit' value='Change'>"
						+ "</form>"
					+ "</div>";

		// replace blank div below logo and market with form
		$(".select-market").replaceWith(form);

		// cancel loading URL
		return false;
	});
});