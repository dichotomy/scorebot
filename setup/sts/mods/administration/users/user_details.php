<?php 
if(isset($_SESSION['user_id'])) { 
	$id = $_GET['id'];
	
	$sql = "SELECT fn, ln, mail, location_id, group_id, acl_id FROM users WHERE id = '$id'";
	$result = mysql_fetch_assoc(mysql_query($sql));
	
	$fn = $result['fn'];
	$ln = $result['ln'];
	$mail = $result['mail'];
	$location_id = $result['location_id'];
	$group_id = $result['group_id'];
	$acl_id = $result['acl_id'];
?>

	<div class="section_780 h_650">
		<div id="server_message">
			<div class="info">
				You can edit the User's details below.  Click the "Save" button when finished.
			</div>
		</div>
		<form name="edit_user" id="edit_user" method="post" action="?p=process_edit_user&id=<?php echo $id; ?>">
			<table class="full">
				<tr><th align="right" width="100">First Name:</th><td><input type="text" name="fn" class="k-textbox full" value="<?php echo $fn; ?>" /></td></tr>
				<tr><th align="right">Last Name:</th><td><input type="text" name="ln" class="k-textbox full" value="<?php echo $ln; ?>" /></td></tr>
				<tr><th align="right">Email:</th><td><input type="text" name="mail" class="k-textbox full" value="<?php echo $mail; ?>" /></td></tr>
				<tr>
					<th align="right"> Location:</th>
					<td>
						<select name="location" id="location_edit" class="full">
							<?php
							$sql = "SELECT * FROM locations WHERE id = '$location_id'";
							$result = mysql_fetch_assoc(mysql_query($sql));
							$name = $result['name'];
							
							echo '<option value='.$location_id.'>'.$name.'</option>';
							
							$sql = "SELECT * FROM locations WHERE type = '1' AND id != '$location_id' ORDER BY name";
							$result = mysql_query($sql);
							echo mysql_error();
							$num = mysql_num_rows($result);
							$i = 0;
							while ($i < $num) {
							
								$id = mysql_result($result, $i, "id");
								$name = mysql_result($result, $i, "name");
								
								echo '<option value='.$id.'>'.$name.'</option>';
							
								$i++;
							}
							?>
						</select>
					</td>
				</tr>
				<tr>
					<th align="right"> Group:</th>
					<td>
						<select name="group" id="group" class="full">
							<?php
							$sql = "SELECT * FROM groups WHERE id = '$group_id'";
							$result = mysql_fetch_assoc(mysql_query($sql));
							$name = $result['name'];
							
							echo '<option value='.$group_id.'>'.$name.'</option>';
							
							$sql = "SELECT * FROM groups WHERE id != '$group_id' ORDER BY name";
							$result = mysql_query($sql);
							echo mysql_error();
							$num = mysql_num_rows($result);
							$i = 0;
							while ($i < $num) {
							
								$id = mysql_result($result, $i, "id");
								$name = mysql_result($result, $i, "name");
								
								echo '<option value='.$id.'>'.$name.'</option>';
							
								$i++;
							}
							?>
						</select>
					</td>
				</tr>
				<tr>
					<th align="right"> Access Level:</th>
					<td>
						<select name="acl" id="acl" class="full">
							<?php
							$sql = "SELECT * FROM acls WHERE id = '$acl_id'";
							$result = mysql_fetch_assoc(mysql_query($sql));
							$name = $result['name'];
							
							echo '<option value='.$acl_id.'>'.$name.'</option>';
							
							$sql = "SELECT * FROM acls WHERE id != '$acl_id' ORDER BY name";
							$result = mysql_query($sql);
							echo mysql_error();
							$num = mysql_num_rows($result);
							$i = 0;
							while ($i < $num) {
							
								$id = mysql_result($result, $i, "id");
								$name = mysql_result($result, $i, "name");
								
								echo '<option value='.$id.'>'.$name.'</option>';
							
								$i++;
							}
							?>
						</select>
					</td>
				</tr>
				<tr><td></td><td align="right"><p>The users password will be sent via email to him/her once the account is created.</td></tr>
				<tr><td align="right" colspan="2"><input type="submit" name="submit" value="Save" class="k-button"/></td></tr>
			</table>
		</form>
	</div>

<script>
// bind form using ajaxForm 
$("#location_edit").width("100%").kendoComboBox();
$("#group").width("100%").kendoComboBox();
$("#acl").width("100%").kendoComboBox();
$('#edit_user').ajaxForm({ 
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