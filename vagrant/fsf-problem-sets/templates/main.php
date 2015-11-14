<html>
<head>
	<title>FluppyBase 9000</title>
	<link href="../static/styles.css" rel="stylesheet">
</head>

<body>

	<section class = "container">

		<!-- logo, header, login -->
		<section = "logo">
			<h1 class = "logo-left">FluppyBase</h1>
			<p class = "logo-center">
				<a href = "{{ url_for('puppies') }}">Our Puppies</a>
				&nbsp; &nbsp;
				<a href = "{{ url_for('shelters') }}">Our Shelters</a>
			</p>
			<p class = "logo-right">
				<a href="{{ url_for('login',login_id=login[0]) }}">{{ login[1] }}</a>
			</p>
		</section>

		<!-- message flashing -->
		<section>
		{% with messages = get_flashed_messages() %}
			{% if messages %}
			<ul>
				{% for message in messages %}
					<li><strong> {{message}} </strong></li>
				{% endfor %}
			</ul>
			{% endif %}
		{% endwith %}
		</section>

		<!-- main app content -->
		<section>
			{{ content }}
		</section>

		<!-- bottom of page -->
		<section class = "footer">
			<p class = "footer">2015 Udacity project by Botmasher (Josh)</p>
		</section>

	<section>

</body>
</html>