<?php
if($_POST['submit'] == 'Login!') {

	$mail = mysql_real_escape_string($_POST['mail']);
	$password = md5($_POST['password']);

	$sql = "SELECT id, fn, ln, acl_id, fpc, group_id, state, login_attempts, location_id"
	." FROM users WHERE mail = '$mail' AND password = '$password'";
	
	$result = mysql_fetch_assoc(mysql_query($sql));
	
	$_SESSION['user_id'] = $result['id'];
	$_SESSION['user_acl'] = $result['acl_id'];
	$_SESSION['fn'] = $result['fn'];
	$_SESSION['ln'] = $result['ln'];
	$_SESSION['login_attempts'] = $result['login_attempts'];
	$_SESSION['fpc'] = $result['fpc'];
	$_SESSION['state'] = $result['state'];
	$_SESSION['group_id'] = $result['group_id'];
	$_SESSION['location_id'] = $result['location_id'];
	
	if(isset($_SESSION['user_id'])) {
		if($_SESSION['user_acl'] > 1) {
			if($_SESSION['fpc'] == 2) {
				header('Location: ?p=change_password');
			} else {
				header('Location: ?p=dashboard');
			}
		}
		if($_SESSION['user_acl'] == 1) {
			if($_SESSION['fpc'] == 2) {
				header('Location: ?p=change_password');
			} else {
				header('Location: ?p=end_user');
			}
		}
	}
	
	
}
?>