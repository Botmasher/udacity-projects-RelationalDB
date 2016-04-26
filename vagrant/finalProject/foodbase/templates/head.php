<html>
<head>
	<title>FoodBase</title>
	<link href="/static/styles.css" rel="stylesheet">
	<link href="/static/bootstrap-theme.min.css" rel="stylesheet">
	<link href="/static/bootstrap.min.css" rel="stylesheet">
	<script src="/static/jquery.min.js"></script>
	<script src="/static/loadentries.js"></script>
	<script src="/static/select-market.js"></script>
</head>
<body>
	<section class = "logo-section">
		<a href="/" class="logo-link"><h1 class = "logo">FoodBase
			<br>
			<div class = "logo-box">&nbsp;</div>
			<div class = "logo-box">&nbsp;</div>
			<div class = "logo-box">&nbsp;</div>
		</h1></a>

		<h2>Restaurants in <a class ="market-link" href="">{{ market }}</a></h2>
		<div class = "select-market"></div>
	</section>