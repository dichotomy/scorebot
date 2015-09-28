<?php if(isset($_SESSION['user_id'])) { ?>

	<div class="section_780 h_650">
		<div id="server_message">
			<div class="info">
				To add a user please complete the form below.  When finished click the "Add User" button.
			</div>
		</div>
		<form name="add_user" id="add_user" method="post" action="?p=process_add_user">
			<table class="full">
				<tr><th align="right" width="100">First Name:</th><td><input type="text" name="fn" class="k-textbox full" /></td></tr>
				<tr><th align="right">Last Name:</th><td><input type="text" name="ln" class="k-textbox full" /></td></tr>
				<tr><th align="right">Email:</th><td><input type="text" name="mail" class="k-textbox full" /></td></tr>
				<tr>
					<th align="right"> Location:</th>
					<td>
						<select name="location" id="location" class="full">
							<?php
							$sql = "SELECT * FROM locations WHERE type = '1' ORDER BY name";
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
							$sql = "SELECT * FROM groups ORDER BY name";
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
							$sql = "SELECT * FROM acls ORDER BY name";
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
				<tr><td align="right" colspan="2"><input type="submit" name="submit" value="Add User" class="k-button"/></td></tr>
			</table>
		</form>
	</div>

<script>
// bind form using ajaxForm 
$("#location").width("100%").kendoComboBox();
$("#group").width("100%").kendoComboBox();
$("#acl").width("100%").kendoComboBox();
$('#add_user').ajaxForm({ 
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