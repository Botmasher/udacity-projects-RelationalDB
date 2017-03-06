<html>
<head>
	<script src = "//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js">
	</script>
	<script src = "https://apis.google.com/js/client:platform.js?onload=start" async defer>
	</script>
</head>

<body>
	<div id = "signinButton">
		<span class = "g-signin"
			data-scope = "openid"
			data-clientid = "430561086760-tdn96ri066dpsbe37fvukakpabbnn5oq.apps.googleusercontent.com"
			data-redirecturi = "postmessage"
			data-accesstype = "offline"
			data-cookiepolicy = "single_host_origin"
			data-callback = "signinCallback"
			data-approvalprompt = "force">
		</span>
	</div>
	<div id = "result"></div>

<script>
function signinCallback (authRes) {
	// if param called 'code', G auth was successful
	if (authRes['code']) {
		// Hide the G signin button
		$('#signinButton').attr('style', 'display: none');
		// ajax call passing the one-time code onto the server
		$.ajax({
			type: 'POST',
			// remember to define gconnect route on our server
			// send state var to use our check against x-site ref forgery
			url: '/gconnect?state={{state}}',
			// tell jQuery not to process the result into str
			processData: false,
			// octet-stream is arbitrary binary stream of data
			contentType: 'application/octet-stream; charset=utf-8',
			data: authRes['code'],
			// 200 code response - log user into app
			success: function(res) {
				console.log ("/login AJAX success!");
				if (res) {
					// populate above empty div with response
					$('#result').html('Login successful!<br>'+res+'<br>Redirecting...');
					setTimeout (function() {
						window.location.href = '/';
					}, 3500);
				}
			}
		});
	} else if (authResult['error']) {
    	console.log('Encountered this error: ' + authResult['error']);
  	} else {
  		$('#result').html('Failed to make server-side call. Check configuration and console.');
    }
}
</script>
</body>
</html>