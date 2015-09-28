<?php

if(isset($_SESSION['user_id'])) {
	if($_POST['submit']) {
	
		$id = $_GET['id'];
	
	
		$err = array();
		$suc = array();
		
		$password = $_POST['password'];
		$confirm = $_POST['confirm'];
		
		if($password != $confirm) {
			$err[] = 'The password did not match.';
		}
		
		if(strlen($password) < 5) {
			$err[] = 'The password was too shoort.';
		}
		
		if($_POST['fpc'] == 'force_change') {
			$fpc = '2';	
		} else {
			$fpc = '1';
		}
		
		if(!count($err)) {
		
			$password = md5($password);
		
			$sql = "UPDATE users SET password = '$password', fpc = '$fpc' WHERE id = '$id'";
			mysql_query($sql);
			echo mysql_error();
			
			$suc[] = 'The Users password has been reset.';
		
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