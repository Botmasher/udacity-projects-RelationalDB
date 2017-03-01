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
</body>

</html>