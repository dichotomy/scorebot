<?php

if(isset($_SESSION['user_id'])) {
	if($_POST['submit']) {
	
		$id = $_GET['id'];
	
		$err = array();
		$suc = array();
		
		$fn = mysql_real_escape_string($_POST['fn']);
		$ln = mysql_real_escape_string($_POST['ln']);
		$mail = mysql_real_escape_string($_POST['mail']);
		$location = mysql_real_escape_string($_POST['location']);
		$group = mysql_real_escape_string($_POST['group']);
		$acl = mysql_real_escape_string($_POST['acl']);
		
		if(strlen($fn) < 3) {
			$err[] = 'The first name used was too short.';
		}
		if(strlen($ln) < 3) {
			$err[] = 'The last name used was too short.';
		}
		if(strlen($mail) < 7) {
			$err[] = 'The email address used was too short.';
		}
		$sql = "SELECT * FROM users WHERE mail = '$mail' AND id != '$id'";
		$num = mysql_num_rows(mysql_query($sql));
		if($num >= 1) {
			$err[] = 'A user with that email already exists.';		
		}

		if(!count($err)) {
		
			//Generate Password
			
			$password = $fn.$ln;
			$db_password = md5($password);
			
		
			//Add the user to the database
			$sql = "UPDATE users SET fn = '$fn', ln = '$ln', mail = '$mail', location_id = '$location', group_id = '$group', acl_id = '$acl' WHERE id = '$id'";
			
			mysql_query($sql);
			echo mysql_error();
			
			$suc[] = 'The user has been updated in the database.';
		
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