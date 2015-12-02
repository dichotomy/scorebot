<?php
define('INCLUDE_CHECK',true);
require_once 'config/connect.php';
include 'config/application_settings.php';

session_name('expressservicedesk');
//session_set_cookie_params('3600');
session_start();

if($_GET['p'] == 'logoff') {
session_start();
session_destroy();
header('Location: ?p=login');
}

include 'mods/login/data/process_login.php';

if(!isset($_SESSION['user_id']) && $_GET['p'] != 'login') {
	header('Location: ?p=login');
}

if(isset($_SESSION['user_id'])) {
	if($_SESSION['user_acl'] > 1) {
		if(!isset($_GET['p'])) {
			header('Location: ?p=dashboard&v=tickets');
		}
	}
}

if(isset($_SESSION['user_id'])) {
	if($_SESSION['user_acl'] > 1) {
		if($_GET['p'] == 'login') {
			header('Location: ?p=dashboard&v=tickets');
		}
	}
}

if(isset($_SESSION['user_id']) && $_GET['p'] == 'dashboard') {
	if(!isset($_GET['v'])) {
		header('Location: ?p=dashboard&v=tickets');
	}
}

if($_SESSION['fpc'] == 2 && $_GET['p'] != 'change_password') {
	if($_GET['p'] != 'process_change_password') {
		header('Location: ?p=change_password');
	}
}

if($_SESSION['user_acl'] == 1) {
	if(!isset($_GET['p'])) {
		header('Location: ?p=end_user');
	}
}

if($_SESSION['user_acl'] == 1) {
	if($_GET['p'] == 'login') {
		header('Location: ?p=end_user');
	}
}



$page = mysql_real_escape_string($_GET['p']);
$sql = "SELECT * FROM mods WHERE name = '$page'";
$num = mysql_num_rows(mysql_query($sql));
if($num > 1 || $num < 1) {
	if($page != 'login') {
		header('Location: ?p=logoff');
		header('Location: ?p=login');
	}
}

$sql = "SELECT * FROM mods WHERE name = '$page'";
$result = mysql_fetch_assoc(mysql_query($sql));
$type = $result['type'];


date_default_timezone_set('America/Chicago');
$date = date('Y-m-d');
$time = date('H:i:s');


$int_date = strtotime($date);
$int_time = strtotime($time);


?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">

<html>
	<head>
	<link rel="icon" 
      type="image/png" 
      href="img/icons/16x16/devices/computer.png">
	<title><?php echo $application_title; ?></title>
	<?php if($type < 4) { ?>
    <script src="js/kendo/jquery.min.js"></script>
    <script src="js/jquery.form.js"></script>
    <script src="js/kendo/kendo.web.min.js"></script>
    <link href="css/kendo/kendo.common.min.css" rel="stylesheet" />
    <link href="css/kendo/kendo.custom.css" rel="stylesheet" />
	<LINK REL=StyleSheet HREF="css/styles.css" TYPE="text/css" MEDIA=all>
	<LINK REL=StyleSheet HREF="css/menu.css" TYPE="text/css" MEDIA=all>
	<LINK REL=StyleSheet HREF="css/login.css" TYPE="text/css" MEDIA=all>
	<LINK REL=StyleSheet HREF="css/messages.css" TYPE="text/css" MEDIA=all>
	<?php } ?>
	</head>
<body>

