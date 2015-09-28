<?php if(isset($_SESSION['user_id'])) { ?>

	<div class="section_780">
		<div id="server_message">
			<div class="info">
				Please specifiy a category name is the field below then click "Add Category".
			</div>
		</div>
		<form name="add_category" id="add_category" method="post" action="?p=process_add_category">
			<table class="form">
				<tr><th>Category:</th><td width="200"><input type="text" name="category" class="k-textbox full" value="<?php echo $_POST['category']; ?>" /></td><td><input type="submit" name="submit" value="Add Category" class="k-button"/></td></tr>
			</table>
		</form>
	</div>

<script>
// bind form using ajaxForm 
$('#add_category').ajaxForm({ 
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