<?php if(isset($_SESSION['user_id'])) { ?>
<?php

	//GET CATEGORY TO EDIT
	
	$id = $_GET['id'];
	
	$sql = "SELECT * FROM groups WHERE id = '$id'";
	$result = mysql_fetch_assoc(mysql_query($sql));
	
	$name = $result['name'];

?>

	<div class="section_780">
		<div id="server_message">
			<div class="info">
				Edit the group below click the "Save Group" button when finished.  To delete click the "Delete" button.
			</div>
		</div>
		<form name="edit_group" id="edit_group" method="post" action="?p=process_edit_group&id=<?php echo $id; ?>">
			<table class="form">
				<tr><th>Group:</th><td width="200"><input type="text" name="name" class="k-textbox full" value="<?php echo $name; ?>" /></td><td><input type="submit" name="submit" value="Save Group" class="k-button"/></td>
			
		</form>
		
		<form name="delete_group" id="delete_group" method="post" action="?p=process_delete_group&id=<?php echo $id; ?>">
		
				<td><input type="submit" name="submit" value="Delete" class="k-button"></td></tr>
		
			</table>
		</form>
	</div>


<script>
// bind form using ajaxForm 
$('#edit_group').ajaxForm({ 
	// target identifies the element(s) to update with the server response 
    target: '#server_message', 
 
    // success identifies the function to invoke when the server response 
    // has been received; here we apply a fade-in effect to the new content 
    success: function() { 
    $('#server_message').fadeIn("slow"); 
            
    } 
});

$('#delete_group').ajaxForm({ 
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