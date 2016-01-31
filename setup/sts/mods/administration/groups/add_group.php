<?php if(isset($_SESSION['user_id'])) { ?>

	<div class="section_780">
		<div id="server_message">
			<div class="info">
				Please specifiy a group name in the field below then click "Add Group".
			</div>
		</div>
		<form name="add_group" id="add_group" method="post" action="?p=process_add_group">
			<table class="form">
				<tr><th>Group:</th><td width="200"><input type="text" name="name" class="k-textbox full" value="<?php echo $_POST['name']; ?>" /></td><td><input type="submit" name="submit" value="Add Group" class="k-button"/></td></tr>
			</table>
		</form>
	</div>

<script>
// bind form using ajaxForm 
$('#add_group').ajaxForm({ 
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