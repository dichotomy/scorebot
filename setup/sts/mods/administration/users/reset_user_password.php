<?php 
if(isset($_SESSION['user_id'])) { 
	$id = $_GET['id'];
	

?>

	<div class="section_780 h_650">
		<div id="server_message_reset">
			<div class="info">
				You can reset the User's password below.  Please click "Save" when you have finished.
			</div>
		</div>
		<form name="reset_password" id="reset_password" method="post" action="?p=process_reset_user_password&id=<?php echo $id; ?>">
			<table class="full">
				<tr><th align="right" width="100">Password:</th><td><input type="password" name="password" class="k-textbox full" value="<?php echo $fn; ?>" /></td></tr>
				<tr><th align="right">Confirm Password:</th><td><input type="password" name="confirm" class="k-textbox full" value="<?php echo $ln; ?>" /></td></tr>
				<tr><th align="right">Force Password Change?:</th><td><input type="checkbox" name="fpc" class="k-checkbox" value="force_change" checked/></td></tr>
				<tr><td align="right" colspan="2"><input type="submit" name="submit" value="Save" class="k-button"/></td></tr>
			</table>
		</form>
	</div>

<script>
// bind form using ajaxForm 

$('#reset_password').ajaxForm({ 
	// target identifies the element(s) to update with the server response 
    target: '#server_message_reset', 
 
    // success identifies the function to invoke when the server response 
    // has been received; here we apply a fade-in effect to the new content 
    success: function() { 
    $('#server_message_reset').fadeIn("slow"); 
            
    } 
});
</script>

<?php } ?>