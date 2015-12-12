$(function () {
	$('a#testAjax').bind('click', function() {
		//var name = $('name').val();
		$.ajax({
			url: 'http://en.wikipedia.org/w/api.php?action=opensearch&search=NYC&format=json&callback=wikiCallback/',
			//data: $('#test-ajax-form').serialize(),
			dataType: 'jsonp',
			success: function(json) {
				$('#temporaryDiv').text('it worked!');
			},
			error: function(e) {
				$('#temporaryDiv').text('it failed!');
			}
		});
		return false;
	});
});