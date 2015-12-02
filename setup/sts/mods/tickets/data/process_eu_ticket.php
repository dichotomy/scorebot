<?php
	$err = array();
	$suc = array();
	
	$subject = mysql_real_escape_string($_POST['subject']);
	$issue = mysql_real_escape_string($_POST['issue']);
	$preview = strip_tags(htmlspecialchars_decode(stripslashes($issue)));
	$preview = mysql_real_escape_string($preview);	
	
	if(strlen($subject) < 5) {
		$err[] = 'The subject was too short.';
	}
	if(strlen($issue) < 5) {
		$err[] = 'The issue was too short.';
	}
	
	if(!count($err)) {
		$sql = "INSERT INTO tickets (subject, issue, preview, created_uid, created_date, created_time, location_id, state_id, eu_uid, category_id) VALUES "
		."('$subject', '$issue', '$preview', '$_SESSION[user_id]', '$int_date', '$int_time', '$_SESSION[location_id]', '1', '$_SESSION[user_id]', '1')";
		
		mysql_query($sql);
		$ticket_id = mysql_insert_id();
		echo mysql_error();
		
		//CREATE NOTIFICATION
		$subject = 'Ticket Created - '.$ticket_id;
		$data = 'This is a confirmation email letting you know that your ticket was successfully created.<br /><br />Ticket ID: '.$ticket_id;
				
		$sql = "INSERT INTO notifications (user_id, subject, data, dt, state) VALUES ("
		."'$_SESSION[user_id]', '$subject', '$data', '$int_date', '1')";
		
		mysql_query($sql);
		echo mysql_error();
		
		$suc[] = 'The ticket has been created.  Thank You!';	
	}
	
	if(count($err)) {
		echo '<div class="error">';
		echo implode('<br /', $err);
		echo '</div>';
	}
	
	if(!count($err)) {
		echo '<div class="success">';
		echo implode('<br /', $suc);
		echo '</div>';
	}
	
?>