$(function () {
	$('a#testAjax').bind('click', function() {
		// grab value from input tag matching this id
		var name = $('#username').val();
		$.ajax({
			// grab test data from wikipedia api
			url: 'http://en.wikipedia.org/w/api.php?action=opensearch&search=NYC&format=json&callback=wikiCallback/',
			
			// serialize submitted form data (previous test)
			//data: $('#test-ajax-form').serialize(),
			dataType: 'jsonp',
			success: function(json) {
				$('#temporaryDiv').text(name+' says: "'+json[2]+'"');
			},
			error: function(e) {
				$('#temporaryDiv').text('<p>'+e+'</p>' + '<p>Failed to load content!</p>');
			}
		});
		return false;
	});
});