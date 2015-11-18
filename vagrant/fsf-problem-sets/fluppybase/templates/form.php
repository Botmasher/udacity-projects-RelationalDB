<html>
<head>
	<title>FluppyBase 9000</title>
	<link href="/static/styles.css" rel="stylesheet">
	<link href="/static/bootstrap-theme.min.css" rel="stylesheet">
	<link href="/static/bootstrap.min.css" rel="stylesheet">
</head>

<body>

	<section class = "center-block container">

		<!-- main block -->

		<!-- logo, header, login -->
		<section class = "header row well">
			<div class="col-md-5 col-xs-12">
				<h1><span class="logo-text">FluppyBase</span><span class="logo-icon">犭</span></h1>
			</div>
			<div class="col-md-3 col-xs-4 menu-item">
				<a href="{{ url_for('puppies') }}">Our Puppies</a>
			</div>
			<div class="col-md-3 col-xs-4 menu-item">
				<a href="{{ url_for('shelters') }}">Our Shelters</a>
			</div>
			<div class="text-right col-md-1 col-xs-2 menu-login">
				<a href="{{ url_for('login',login_id=login[0]) }}">{{ login[1] }}</a>
			</div>
		</section>

		<section class = "main row">
			<!-- message flashing -->
			<div>
			{% with messages = get_flashed_messages() %}
				{% if messages %}
				<ul>
					{% for message in messages %}
						<li><strong> {{message}} </strong></li>
					{% endfor %}
				</ul>
				{% endif %}
			{% endwith %}
			</div>

			<!-- app form -->
			{% from "_formhelpers.html" import render_field %}
			<form method="POST" action="">
			  <dl>
			    {{ render_field(form.username) }}
			    {{ render_field(form.email) }}
			    {{ render_field(form.password) }}
			    {{ render_field(form.accept_tos) }}
			  </dl>
			  <p><input type="submit" value="Register"></p>
			</form>
		</section>

		<!-- bottom of page -->
		<section class = "footer well">
			<p>2015 Udacity project by Botmasher (Josh)</p>
		</section>

	</section>

</body>
</html>