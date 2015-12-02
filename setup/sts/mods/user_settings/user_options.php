<?php if(isset($_SESSION['user_id'])) { ?>
<div class="section_960">

	<div class="section_125_l">
		<?php include 'user_options_menu.php'; ?>
	</div>
	
	<div class="section_780_r" id="gridWrapper">
		<div id="server_message">
		<?php
		if($_SESSION['fpc'] == 2) {
			echo '<div class="warning">';
			echo 'You are required to change your password before you can continue.';
			echo '</div>';		
		} else {
			echo '<div class="info">';
			echo 'To change your password complete the form below.  When you are ready click the "Change Password" button.';
			echo '</div>';
		}
		?>
		</div>
		<form name="change_password" id="change_password" method="post" action="?p=process_change_password&id=<?php echo $_SESSION['user_id']; ?>">
			<table>
				<tr><td>New Password:</td><td width="250"><input type="password" name="new_password" class="k-textbox full" /></td></tr>
				<tr><td>Confirm Password:</td><td width="250"><input type="password" name="confirm_password" class="k-textbox full" /></td></tr>
				<tr><td colspan="2" align="right"><input type="submit" name="submit" value="Change Password" class="k-button" /></td></tr>
			</table>
		</form>
	</div>
</div>

<script>
$('#change_password').ajaxForm({ 
	// target identifies the element(s) to update with the server response 
    target: '#server_message', 
 
    // success identifies the function to invoke when the server response 
    // has been received; here we apply a fade-in effect to the new content 
    success: function() { 
    $('#server_message').fadeIn("slow"); 
            
    } 

});
</script>


<?php } ?>