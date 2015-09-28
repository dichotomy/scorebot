<?php
	
	//Application Title
	$sql = "SELECT * FROM application_settings WHERE name = 'title'";
	$result = mysql_fetch_assoc(mysql_query($sql));
	$application_title = $result['setting'];
	
	//Application Root
	$application_root = "http://localhost/sts/index.php";

?>