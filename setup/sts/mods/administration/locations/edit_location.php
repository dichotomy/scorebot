<?php if(isset($_SESSION['user_id'])) { ?>
<?php

	//GET CATEGORY TO EDIT
	
	$id = $_GET['id'];
	
	$sql = "SELECT * FROM locations WHERE id = '$id'";
	$result = mysql_fetch_assoc(mysql_query($sql));
	
	$name = $result['name'];

?>

	<div class="section_780">
		<div id="server_message">
			<div class="info">
				Edit the category below click the "Save Category" button when finished.  To delete click the "Delete" button.
			</div>
		</div>
		<form name="edit_location" id="edit_location" method="post" action="?p=process_edit_location&id=<?php echo $id; ?>">
			<table class="form">
				<tr><th>Location:</th><td width="200"><input type="text" name="name" class="k-textbox full" value="<?php echo $name; ?>" /></td><td><input type="submit" name="submit" value="Save Location" class="k-button"/></td>
			
		</form>
		
		<form name="delete_location" id="delete_location" method="post" action="?p=process_delete_location&id=<?php echo $id; ?>">
		
				<td><input type="submit" name="submit" value="Delete" class="k-button"></td></tr>
		
			</table>
		</form>
	</div>


<script>
// bind form using ajaxForm 
$('#edit_location').ajaxForm({ 
	// target identifies the element(s) to update with the server response 
    target: '#server_message', 
 
    // success identifies the function to invoke when the server response 
    // has been received; here we apply a fade-in effect to the new content 
    success: function() { 
    $('#server_message').fadeIn("slow"); 
            
    } 
});

$('#delete_location').ajaxForm({ 
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