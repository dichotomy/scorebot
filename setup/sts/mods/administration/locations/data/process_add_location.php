<?php

if(isset($_SESSION['user_id'])) {
	if($_POST['submit']) {
	
		$err = array();
		$suc = array();
		
		$name = $_POST['name'];
		$name = mysql_real_escape_string($name);
		
		$sql = "SELECT * FROM categories WHERE category = '$category'";
		$num = mysql_num_rows(mysql_query($sql));
		
		if($num >= 1) {
		
			$err[] = 'A location with that name already exists in the database.';
		
		}
		if(strlen($name) < 3) {
		
			$err[] = 'The location field was left blank or was too short!';
		
		}
		
		if(!count($err)) {
		
			$sql = "INSERT INTO locations (name) VALUES ('$name')";
			mysql_query($sql);
			echo mysql_error();
		
			$suc[] = 'The location has been added to the database.';
		
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