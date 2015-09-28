<?php
include 'header.php';
$page = mysql_real_escape_string($_GET['p']);
$sql = "SELECT * FROM mods WHERE name = '$page'";
$result = mysql_fetch_assoc(mysql_query($sql));
$type = $result['type'];

if(isset($_SESSION['user_id'])) {
	if($type < 2) {
		include 'mods/menu/top.php';
	}

	$mod = $_GET['p'];
	
	$sql = "SELECT * FROM mods WHERE name = '$mod'";
	$result = mysql_fetch_assoc(mysql_query($sql));
	
	$acl = $result['acl'];
	$path = $result['path'];
	$type = $result['type'];
	
	if($acl <= $_SESSION['user_acl']) {
	
		include 'mods/'.$path;
	
	} else {
			
		echo 'You do not have access to this resource.';
	
	}
}

if(!isset($_SESSION['user_id']) && $_GET['p'] == 'login') {
	include 'mods/login/login.php';
}
	
include 'footer.php';
?>