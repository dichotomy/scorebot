<?php if(isset($_SESSION['user_id'])) { ?>

	<div class="section_780 h_650">
		<div id="server_message">
			<div class="info">
				Please fill out the form below.  Click "Create Ticket" once you are finished.
			</div>
		</div>
		<form name="create_ticket" id="create_ticket" method="post" action="?p=process_create_ticket">
			<table class="full">
				<tr><th align="left" colspan="2">Subject</th></tr>
				<tr><td colspan="2"><input type="text" name="subject" id="subject" class="k-textbox full" /></td></tr>
				<tr><th align="left" colspan="2">Issue</th></tr>
				<tr><td colspan="2"><textarea class="full k-textbox" name="issue" id="issue"></textarea></td></tr>
				<tr><th align="left"> End User:</th><th align="left"> Category:</th></tr>
					<td width="280">
						<select name="eu_id" id="eu_id" class="full">
							<option value="null"></option>
							<?php
							$sql = "SELECT id, mail FROM users WHERE id != '1' ORDER BY mail";
							$result = mysql_query($sql);
							echo mysql_error();
							$num = mysql_num_rows($result);
							$i = 0;
							while ($i < $num) {
							
								$id = mysql_result($result, $i, "id");
								$mail = mysql_result($result, $i, "mail");

								
								echo '<option value='.$id.'>'.$mail.'</option>';
							
								$i++;
							}
							?>
						</select>
					</td>
					<td>
						<select name="category_id" id="category" class="full">
							<option value="null"></option>
							<?php
							$sql = "SELECT * FROM categories ORDER BY category";
							$result = mysql_query($sql);
							echo mysql_error();
							$num = mysql_num_rows($result);
							$i = 0;
							while ($i < $num) {
							
								$id = mysql_result($result, $i, "id");
								$category = mysql_result($result, $i, "category");
								
								echo '<option value='.$id.'>'.$category.'</option>';
							
								$i++;
							}
							?>
						</select>
					</td>
				
				<tr>

				</tr>
				<tr><th align="left"> Location:</th><th align="left"> Group or User Assignement:</th></tr>
					<td width="280">
						<select name="location_id" id="location" class="full">
							<option value="null"></option>
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
					<td>
						<select name="group_id" id="group" class="full">
							<option value="0">No Group Assignment</option>
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
				
				<tr>

				</tr>
				<tr>
					<th></th>
					<td>
						<select name="assigned_uid" id="assigned_uid" class="full">
							<option value="0">No User Assignment</option>
							<?php
							$sql = "SELECT id, mail FROM users WHERE acl_id >= '2' AND id != '1' ORDER BY mail";
							$result = mysql_query($sql);
							echo mysql_error();
							$num = mysql_num_rows($result);
							$i = 0;
							while ($i < $num) {
							
								$id = mysql_result($result, $i, "id");
								$mail = mysql_result($result, $i, "mail");
								
								echo '<option value='.$id.'>'.$mail.'</option>';
							
								$i++;
							}
							?>
						</select>
					</td>
				</tr>
				<tr><td></td><td align="right"><p>You can assign a ticket to a group or a user (tech or higher), not both.</td></tr>
				<tr><td align="right" colspan="2"><input type="submit" name="submit" value="Create Ticket" class="k-button" onclick="createGrid()"/></td></tr>
			</table>
		</form>
	</div>

<script>
//bind form using ajaxForm 
$("#issue").kendoEditor({
	encoded: false
});
$("#eu_id").width("100%").kendoComboBox();
$("#category").width("100%").kendoComboBox();
$("#location").width("100%").kendoComboBox();
$("#group").width("100%").kendoComboBox();
$("#assigned_uid").width("100%").kendoComboBox();
$('#create_ticket').ajaxForm({ 
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