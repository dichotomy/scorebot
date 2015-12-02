<div class="login">
	<h1><?php echo $application_title; ?></h1>
	<form name="login" method="post" action="">
		<table class="full" border="0">
		<tr><td colspan="2"><input type="text" name="mail" id="user_name" class="k-textbox" placeholder="Email Address"/></td></tr>
		<tr><td colspan="2"><input type="password" name="password" id="password" class="k-textbox" placeholder="Password"/></td></tr>
		<tr><td><a href="?p=forgot_password" id="fp_button" class="k-button">Forgot Password</a></td><td><input type="submit" id="login_button" name="submit" value="Login!" class="k-button" /></td></tr>
		</table>
	</form>
</div>