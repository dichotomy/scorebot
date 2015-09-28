<?php
if(isset($_SESSION['user_id'])) {
	if($_POST['submit']) {
	
		$id = $_GET['id'];
		
		$sql = "UPDATE tickets SET state_id = '2', resolved_uid = '$_SESSION[user_id]', "
		."resolved_date = '$int_date', resolved_time = '$int_time' WHERE id = '$id'";
		mysql_query($sql);
		echo mysql_error();
			
		//Log Change
		$data = 'Ticket Closed.';
		$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
		."'$id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
		mysql_query($sql);
		
		
		
		echo '<div class="success">';
		echo 'The ticket has been closed';
		echo '</div>';
	
	}
}
?>