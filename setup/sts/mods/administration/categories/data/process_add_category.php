<?php

if(isset($_SESSION['user_id'])) {
	if($_POST['submit']) {
	
		$err = array();
		$suc = array();
		
		$category = $_POST['category'];
		$category = mysql_real_escape_string($category);
		
		$sql = "SELECT * FROM categories WHERE category = '$category'";
		$num = mysql_num_rows(mysql_query($sql));
		
		if($num >= 1) {
		
			$err[] = 'A Category with that name already exists in the database.';
		
		}
		if(strlen($category) < 3) {
		
			$err[] = 'The Cateogry field was left blank or was too short!';
		
		}
		
		if(!count($err)) {
		
			$sql = "INSERT INTO categories (category) VALUES ('$category')";
			mysql_query($sql);
			echo mysql_error();
		
			$suc[] = 'The Category has been added to the database.';
		
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