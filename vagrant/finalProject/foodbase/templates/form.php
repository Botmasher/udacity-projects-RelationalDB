{% include "head.php" ignore missing %}

	<section>
		<!-- app form -->
		{% from "_formhelpers.html" import render_field %}
		<form method="POST" action="">
		  <dl>
		  	{% for i in form %}
		    	{{ render_field(i) }}
		    {% endfor %}
		  </dl>
		  <p><input type="submit" value="Submit"></p>
		</form>

		{% if content %}{{ content }}{% endif %}
	</section>

	<!-- bottom of page -->
	<section class = "footer well">
		<p>2015 Udacity project by Botmasher (Josh)</p>
	</section>

</body>
</html>