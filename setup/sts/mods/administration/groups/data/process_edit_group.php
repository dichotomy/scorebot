<?php
if(isset($_SESSION['user_id'])) {
	$id = $_GET['id'];

	if($_POST['submit']) {
	
		$err = array();
		$suc = array();
		
		$name = $_POST['name'];
		$name = mysql_real_escape_string($name);
		
		$sql = "SELECT * FROM groups WHERE name = '$name' AND id != '$id'";
		$num = mysql_num_rows(mysql_query($sql));
		
		if($num >= 1) {
		
			$err[] = 'A group with that name already exists in the database.';
		
		}
		if(strlen($name) < 3) {
		
			$err[] = 'The group field was left blank or was too short!';
		
		}
		
		if(!count($err)) {
		
			$sql = "UPDATE groups SET name = '$name' WHERE id = '$id'";
			mysql_query($sql);
			echo mysql_error();
		
			$suc[] = 'The group has been updated in the database.';
		
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