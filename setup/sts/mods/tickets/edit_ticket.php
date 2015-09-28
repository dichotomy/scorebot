<?php 
if(isset($_SESSION['user_id'])) { 

	$id = mysql_real_escape_string($_GET['id']);
	$tid = mysql_real_escape_string($_GET['id']);
	
	$sql = "SELECT tickets.issue, tickets.state_id, tickets.created_uid, tickets.category_id, tickets.assigned_uid, "
	."tickets.assigned_gid, tickets.location_id, tickets.eu_uid, users.mail, tickets.created_date, "
	."tickets.created_time, categories.category, locations.name AS location_name "
	."FROM tickets, users, categories, locations, states WHERE users.id = tickets.created_uid AND tickets.id = '$id' "
	."AND tickets.category_id = categories.id AND locations.id = tickets.location_id";
	$result = mysql_fetch_assoc(mysql_query($sql));
	echo mysql_error();
	
	$ticket_created_by = $result['mail'];
	$issue = $result['issue'];
	$created_date = $result['created_date'];
	$created_date = date('m/d/Y', $created_date);
	$created_time = $result['created_time'];
	$created_time = date('H:i:s', $created_time);
	$category_id = $result['category_id'];
	$category = $result['category'];
	$location_id = $result['location_id'];
	$location_name = $result['location_name'];
	$assigned_gid = $result['assigned_gid'];
	if($assigned_gid == 0) {
		$assigned_gid = 0;
		$assigned_gn = 'No Group Assignment';
	}
	$assigned_uid = $result['assigned_uid'];
	$state_id = $result['state_id'];
	
		
?>
	<div class="section_780 h_650">
		<form name="edit_ticket" <?php if($state == 1) { echo 'class="float_right"'; } ?> id="edit_ticket<?php echo $tid; ?>" method="post" action="?p=process_edit_ticket&id=<?php echo $id; ?>">
			<table class="full">
				<tr><th align="left" colspan="2">Issue / Notes</th></tr>
				<tr><td colspan="2">
					
					<div id="issue_notes<?php echo $tid; ?>">
						<div id="server_message<?php echo $tid; ?>">
						<div>
							<?php

								echo '<p class="notes_date">'.$created_date.'  '.$created_time.'</p>';
								echo '<p class="notes_user">'.$ticket_created_by.'</p>';
								echo '<div class="clear"></div>';
								echo '<p class="notes_issue">'.$issue.'</p>';
								$sql = "SELECT * FROM tickets_log, users WHERE user_id = id AND ticket_id = '$id'";
								$result = mysql_query($sql);
								$num = mysql_num_rows($result);
								$i = 0;
								while ($i < $num) {
								
									$data = mysql_result($result, $i, "data");
									$mail = mysql_result($result, $i, "mail");
									$log_date = mysql_result($result, $i, "date");
									$log_time = mysql_result($result, $i, "time");
									$log_date = date('m/d/Y', $log_date);
									$log_time = date('H:i:s', $log_time);
									
									echo '<p class="notes_date">'.$log_date.'  '.$log_time.'</p>';
									echo '<p class="notes_user">'.$mail.'</p>';
									echo '<div class="clear"></div>';
									echo '<p class="notes_issue">'.$data.'</p>';

									
									$i++;
								}
							?>
						</div>
						</div>
					</div>
				</td></tr>
				<?php if($state_id == 1) { ?>
				<tr><th align="left" colspan="2">Update Ticket</th></tr>
				<tr><td colspan="2"><textarea class="full k-textbox" name="update_ticket" id="update_ticket<?php echo $id; ?>"></textarea></td></tr>
				<tr><th align="left"> End User:</th><th align="left"> Category:</th></tr>
					<td width="280">
						<select name="eu_id" id="eu_id<?php echo $tid; ?>" class="full">
							<?php
							$sql = "SELECT users.id, users.mail FROM users, tickets WHERE users.id = tickets.eu_uid AND tickets.id = '$id'";
							$result = mysql_fetch_assoc(mysql_query($sql));
							$eu_id = $result['id'];
							$mail = $result['mail'];
							echo '<option value='.$eu_id.'>'.$mail.'</option>';
							$sql = "SELECT id, mail FROM users WHERE id != '1' AND id != '$eu_id' ORDER BY mail";
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
						<select name="category_id" id="category<?php echo $tid; ?>" class="full">
							<?php
							echo '<option value='.$category_id.'>'.$category.'</option>';
							$sql = "SELECT * FROM categories WHERE id != '$category_id' ORDER BY category";
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
				<tr><th align="left"> Location:</th><th align="left"> Group or User Assignement:</th></tr>
					<td width="280">
						<select name="location_id" id="location<?php echo $tid; ?>" class="full">
							<?php
							echo '<option value='.$location_id.'>'.$location_name.'</option>';
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
					<td>
						<select name="group_id" id="group<?php echo $tid; ?>" class="full">
							<?php
							if($assigned_gid == 0) {
								echo '<option value="0">No Group Assignment</option>';
							} else {
								$sql = "SELECT id, name FROM groups WHERE id = '$assigned_gid'";
								$result = mysql_fetch_assoc(mysql_query($sql));
								$group_id = $result['id'];
								$group_name = $result['name'];
								echo '<option value='.$group_id.'>'.$group_name.'</option>';
							}
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
					<th></th>
					<td>
						<select name="assigned_uid" id="assigned_uid<?php echo $tid; ?>" class="full">
							<?php
							if($assigned_uid == 0) {
								echo '<option value="0">No User Assignment</option>';
							} else {
								$sql = "SELECT id, mail FROM users WHERE id = '$assigned_uid'";
								$result = mysql_fetch_assoc(mysql_query($sql));
								$assigned_uid = $result['id'];
								$assigned_mail = $result['mail'];
								echo '<option value='.$assigned_uid.'>'.$assigned_mail.'</option>';
							}
							$sql = "SELECT id, mail FROM users WHERE acl_id >= '2' AND id != '1' AND id != '$assigned_uid' ORDER BY mail";
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
				
				<tr><td></td><td align="right"><p>If you switch from Group Assigment to User Assignment the Group Assignment will be removed. This applies for User to Group also.</td></tr>
				<tr><td align="right" colspan="2"><input type="submit" name="submit" value="Update Ticket" class="k-button"/>

			</form>
			<form name="close_ticket" class="float_right" id="close_ticket<?php echo $tid; ?>" method="post" action="?p=process_close_ticket&id=<?php echo $_GET['id']; ?>">
					<input type="submit" name="submit" value="Close Ticket" class="k-button" />
			</form>
				</td>
				</tr>
				<?php } ?>
			</table>
		
		
	</div>

<script>
$(document).ready(function(){
$("#issue_notes<?php echo $tid; ?>").kendoSplitter();
$("#update_ticket<?php echo $tid; ?>").kendoEditor({
	encoded: false
});
$("#eu_id<?php echo $tid; ?>").width("100%").kendoComboBox();
$("#category<?php echo $tid; ?>").width("100%").kendoComboBox();
$("#location<?php echo $tid; ?>").width("100%").kendoComboBox();
$("#group<?php echo $tid; ?>").width("100%").kendoComboBox();
$("#assigned_uid<?php echo $tid; ?>").width("100%").kendoComboBox();

$('#edit_ticket<?php echo $tid; ?>').ajaxForm({ 
	// target identifies the element(s) to update with the server response 
    target: '#server_message<?php echo $tid; ?>', 
 
    // success identifies the function to invoke when the server response 
    // has been received; here we apply a fade-in effect to the new content 
    success: function() { 
    $('#server_message<?php echo $tid; ?>').fadeIn("slow"); 
            
    } 

});
$('#close_ticket<?php echo $tid; ?>').ajaxForm({ 
	// target identifies the element(s) to update with the server response 
    target: '#server_message<?php echo $tid; ?>', 
 
    // success identifies the function to invoke when the server response 
    // has been received; here we apply a fade-in effect to the new content 
    success: function() { 
    $('#server_message<?php echo $tid; ?>').fadeIn("slow"); 
            
    } 

});
});
</script>

<?php } ?>