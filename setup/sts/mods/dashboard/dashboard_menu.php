<?php if(isset($_SESSION['user_id'])) { ?>
	<h1>Dashboard</h1>
	<p><a href="?p=dashboard&v=tickets" id="add_category">Tickets</a></p>
	<p><a href="?p=dashboard&v=tech_status" id="add_category">Tech Status</a></p>
<?php } ?>