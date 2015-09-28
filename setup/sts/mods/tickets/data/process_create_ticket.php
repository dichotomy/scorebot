<?php

if(isset($_SESSION['user_id'])) {
	if($_POST['submit']) {
	
		
	
		$err = array();
		$suc = array();
		
		$subject = mysql_real_escape_string($_POST['subject']);
		$issue = mysql_real_escape_string($_POST['issue']);
		$location_id = mysql_real_escape_string($_POST['location_id']);
		$category_id = mysql_real_escape_string($_POST['category_id']);
		$group_id = mysql_real_escape_string($_POST['group_id']);
		$assigned_uid = mysql_real_escape_string($_POST['assigned_uid']);
		$eu_id = mysql_real_escape_string($_POST['eu_id']);
		
		$preview = strip_tags(htmlspecialchars_decode(stripslashes($issue)));
		$preview = mysql_real_escape_string($preview);
		if(strlen($issue) < 5) {
			$err[] = 'The subject was too short or left blank';
		}		
		if(strlen($issue) < 5) {
			$err[] = 'The issue was too short or left blank';
		}
		if($location_id == 'null') {
			$err[] = 'A location is required';
		}
		if($category_id == 'null') {
			$err[] = 'A category is required';
		}
		if($eu_id == 'null') {
			$err[] = 'A end user is required';
		}
		if($group_id > 0 && $assigned_uid > 0) {
			$err[] = 'You can only assign a ticket to a group or a user, not both.';
		}
		
		if(!count($err)) {
		
			$sql = "INSERT INTO tickets (subject, issue, preview, location_id, category_id, "
			."state_id, created_uid, created_date, created_time, eu_uid) VALUES ("
			."'$subject', '$issue', '$preview', '$location_id', '$category_id', '1', '$_SESSION[user_id]', "
			."'$int_date', '$int_time', '$eu_id')";
			
			mysql_query($sql);
			echo mysql_error();
			
			$ticket_id = mysql_insert_id();
			
			//Log ticket creation
			//$data = '<strong>Ticket Created</strong>';
			//$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
			//."'$ticket_id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
			//mysql_query($sql);
			//Check to see if ticket was assigned...  
			if($group_id > 0) {
				$sql = "UPDATE tickets SET assigned_gid = '$group_id', assigned_uid = '0', "
				."assigned_date = '$int_date', assigned_time = '$int_time' WHERE id = '$ticket_id'";
				mysql_query($sql);
				echo mysql_error();
				$sql = "SELECT * FROM groups WHERE id = '$group_id'";
				$result = mysql_fetch_assoc(mysql_query($sql));
				$group_name = $result['name'];
				$data = 'Assigned to group: '.$group_name;
				$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
				."'$ticket_id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
				mysql_query($sql);
				echo mysql_error();
			}
			if($assigned_uid > 0) {
				$sql = "UPDATE tickets SET assigned_uid = '$assigned_uid', assigned_gid = '0', "
				."assigned_date = '$int_date', assigned_time = '$int_time' WHERE id = '$ticket_id'";
				mysql_query($sql);
				echo mysql_error();
				$sql = "SELECT mail FROM users WHERE id = '$assigned_uid'";
				$result = mysql_fetch_assoc(mysql_query($sql));
				$mail = $result['mail'];
				$data = 'Assigned to user: '.$mail;
				$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
				."'$ticket_id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
				mysql_query($sql);
			}
			
			$suc[] = 'The ticket was created.';
		
		}
	
	}
	
	if(count($err)) {
		echo '<div class="error">';
		echo implode('<br />', $err);
		echo '</div>';
	
	}
	if(count($suc)) {
		echo '<div class="success">';
		echo implode('<br />', $suc);
		echo '</div>';
	
	}
	
}

?>