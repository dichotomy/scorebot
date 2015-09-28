<?php

if(isset($_SESSION['user_id'])) {
	if($_POST['submit']) {
	
		$ticket_id = $_GET['id'];
		$sql = "SELECT * FROM tickets WHERE id = '$ticket_id'";
		$result = mysql_fetch_assoc(mysql_query($sql));
		$old_group_id = $result['assigned_gid'];
		$old_assigned_uid = $result['assigned_uid'];
		$old_category_id = $result['category_id'];
		$old_location_id = $result['location_id'];
		$old_eu_uid = $result['eu_uid'];
		
		
	
		$err = array();
		$suc = array();
		
		$update_ticket = mysql_real_escape_string($_POST['update_ticket']);
		$location_id = mysql_real_escape_string($_POST['location_id']);
		$category_id = mysql_real_escape_string($_POST['category_id']);
		$group_id = mysql_real_escape_string($_POST['group_id']);
		$assigned_uid = mysql_real_escape_string($_POST['assigned_uid']);
		$eu_id = mysql_real_escape_string($_POST['eu_id']);
		
		
			
		
		if($location_id == 'null') {
			$err[] = 'A location is required';
		}
		if($category_id == 'null') {
			$err[] = 'A category is required';
		}
		if($eu_id == 'null') {
			$err[] = 'A end user is required';
		}

		
		if(!count($err)) {
			if(strlen($update_ticket) >= 1) {
				//Add UPDATE TICKET TO LOG
				$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
				."'$ticket_id', '$_SESSION[user_id]', '$update_ticket', '$int_date', '$int_time')";
				mysql_query($sql);
			}
			//Check to see if end user changed	
			if($eu_id != $old_eu_uid) {
				
				$sql = "SELECT * FROM users WHERE id = '$eu_id'";
				$result = mysql_fetch_assoc(mysql_query($sql));
				$mail = $result['mail'];
				
				$sql = "UPDATE tickets SET eu_uid = '$eu_id' WHERE id = '$ticket_id'";
				mysql_query($sql);
				
				//Log Change
				$data = 'End User Changed: '.$mail.'.';
				$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
				."'$ticket_id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
				mysql_query($sql);
			
			}

			//Check to see if location changed	
			if($location_id != $old_location_id) {
				
				$sql = "SELECT * FROM locations WHERE id = '$location_id'";
				$result = mysql_fetch_assoc(mysql_query($sql));
				$name = $result['name'];
				
				$sql = "UPDATE tickets SET location_id = '$location_id' WHERE id = '$ticket_id'";
				mysql_query($sql);
				
				//Log Change
				$data = 'Location changed to: '.$name.'.';
				$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
				."'$ticket_id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
				mysql_query($sql);
		
			}			
			//Check to see if category changed	
			if($category_id != $old_category_id) {
				
				$sql = "SELECT * FROM categories WHERE id = '$category_id'";
				$result = mysql_fetch_assoc(mysql_query($sql));
				$name = $result['category'];
				
				$sql = "UPDATE tickets SET category_id = '$category_id' WHERE id = '$ticket_id'";
				mysql_query($sql);
				
				//Log Change
				$data = 'Category changed to: '.$name.'.';
				$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
				."'$ticket_id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
				mysql_query($sql);
		
			}	
			//Check to see if assignment changed form user to group		
			if($old_group_id == 0 && $group_id > 0) {
		
				//$assigned_uid = 0;
				$sql = "UPDATE tickets SET assigned_uid = '0', assigned_gid = '$group_id' WHERE id = '$ticket_id'";
				mysql_query($sql);
				//Log Change
				$data = 'Assignment changed from user to group.';
				$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
				."'$ticket_id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
				mysql_query($sql);
		
			}
			//Check to see if assignment changed form group to user		
			if($old_assigned_uid == 0 && $assigned_uid > 0) {
		
				//$group_id = 0;
				$sql = "UPDATE tickets SET assigned_uid = '$assigned_uid', assigned_gid = '0' WHERE id = '$ticket_id'";
				mysql_query($sql);

				//Log Change
				$data = 'Assignment changed from group to user.';
				$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
				."'$ticket_id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
				mysql_query($sql);
		
			}
			
			//Update group
			if($old_group_id > 0) {
				if($group_id != $old_group_id) {
					$sql = "SELECT * FROM groups WHERE id = '$group_id'";
					$result = mysql_fetch_assoc(mysql_query($sql));
					$name = $result['name'];
				
					$sql = "UPDATE tickets SET assigned_gid = '$group_id' WHERE id = '$ticket_id'";
					mysql_query($sql);
				
					//Log Change
					$data = 'Group Assignment changed to: '.$name.'.';
					$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
					."'$ticket_id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
					mysql_query($sql);				
				}
			}
			//Update user
			if($old_assigned_uid > 0) {
				if($assigned_uid != $old_assigned_uid) {
					$sql = "SELECT * FROM users WHERE id = '$assigned_uid'";
					$result = mysql_fetch_assoc(mysql_query($sql));
					$mail = $result['mail'];
				
					$sql = "UPDATE tickets SET assigned_uid = '$assigned_uid' WHERE id = '$ticket_id'";
					mysql_query($sql);
				
					//Log Change
					$data = 'User Assignment changed to: '.$mail.'.';
					$sql = "INSERT INTO tickets_log (ticket_id, user_id, data, date, time) VALUES ("
					."'$ticket_id', '$_SESSION[user_id]', '$data', '$int_date', '$int_time')";
					mysql_query($sql);				
				}
			}
			
			$id = $_GET['id'];
			$sql = "SELECT tickets.issue, tickets.created_uid, tickets.category_id, tickets.assigned_uid, "
			."tickets.assigned_gid, tickets.location_id, tickets.eu_uid, users.mail, tickets.created_date, "
			."tickets.created_time, categories.category, locations.name AS location_name "
			."FROM tickets, users, categories, locations WHERE users.id = tickets.created_uid AND tickets.id = '$id' "
			."AND tickets.category_id = categories.id AND locations.id = tickets.location_id";
			$result = mysql_fetch_assoc(mysql_query($sql));
			echo mysql_error();
	
			$ticket_created_by = $result['mail'];
			$issue = $result['issue'];
			$created_date = $result['created_date'];
			$created_date = date('m/d/Y', $created_date);
			$created_time = $result['created_time'];
			$created_time = date('H:i:s', $created_time);
				echo'	<div id="issue_notes">
						<div>';
								echo '<p class="notes_date">'.$created_date.'  '.$created_time.'</p>';
								echo '<p class="notes_user">'.$ticket_created_by.'</p>';
								echo '<div class="clear"></div>';
								echo '<p class="notes_issue">'.$issue.'</p>';
								$sql = "SELECT * FROM tickets_log, users WHERE user_id = id AND ticket_id = '$id'";
								$result = mysql_query($sql);
								$num = mysql_num_rows($result);
								$i = 0;
								while ($i < $num) {
								
									$data = mysql_result($result, $i, "data");
									$mail = mysql_result($result, $i, "mail");
									$log_date = mysql_result($result, $i, "date");
									$log_time = mysql_result($result, $i, "time");
									$log_date = date('m/d/Y', $log_date);
									$log_time = date('H:i:s', $log_time);
									
									echo '<p class="notes_date">'.$log_date.'  '.$log_time.'</p>';
									echo '<p class="notes_user">'.$mail.'</p>';
									echo '<div class="clear"></div>';
									echo '<p class="notes_issue">'.$data.'</p>';

									
									$i++;
								}
							
					echo '</div>
					</div>';
		
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