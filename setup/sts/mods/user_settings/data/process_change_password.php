<?php

if(isset($_SESSION['user_id'])) {
	if($_POST['submit']) {
	
		$new_password = $_POST['new_password'];
		$confirm_password = $_POST['confirm_password'];
		
		if(strlen($new_password) < 4) {
			$err[] = 'The new password is too short...';		
		}
		
		if($new_password != $confirm_password) {
			$err[] = 'The passwords did not match, please try again!';
		}
		
		
		if(!count($err)) {
		
			$password = md5($new_password);
			
			$update = "UPDATE users SET password = '$password', fpc = '1' WHERE id = '$_SESSION[user_id]'";
			mysql_query($update);
			//echo $update;
			echo mysql_error();
			
			$_SESSION['fpc'] = 1;
			
			$suc[] = 'Your password has been changed!';
		
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