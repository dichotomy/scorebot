<?php if(isset($_SESSION['user_id'])) { ?>
<div class="section_960">

	<div class="section_125_l">
		<?php include 'permissions_menu.php'; ?>
	</div>
	
	<div class="section_780_r" id="gridWrapper">
		<div id="server_message">
		</div>
		<form name="update_permisssions" id="update_permisssions" method="post" action="?p=process_update_permissions">
		<table>
			<?php
				$sql = "SELECT mods.name, mods.display, acls.id, acls.name FROM "
				."mods, acls WHERE mods.acl = acls.id AND type != '3' AND type != '4' AND enabled = '1' ORDER BY mods.name";
				$result = mysql_query($sql);
				echo mysql_error();
				$num = mysql_num_rows($result);
				$i = 0;
				
				while ($i < $num) {
				
					$name = mysql_result($result, $i, "name");
					$display = mysql_result($result, $i, "display");
					$c_acl_id = mysql_result($result, $i, "acls.id");
					$c_acl_name = mysql_result($result, $i, "acls.name");										
					
					echo '<tr>';
						echo '<td>';
							echo $display;
						echo '</td>';
						echo '<td>';
							echo '<select name="'.$name.'_acl" id="'.$name.'_acl">';
								echo '<option value="'.$c_acl_id.'">'.$c_acl_name.'</option>';
								$acls = "SELECT * FROM acls WHERE id != '1' AND id != '$c_acl_id'";
								$acls_r = mysql_query($acls);
								$alcs_n = mysql_num_rows($acls_r);
								$n = 0;
								
								while ($n < $alcs_n) {
								
									$acl_id = mysql_result($acls_r, $n, "id");
									$acl_name = mysql_result($acls_r, $n, "name");
									
									echo '<option value="'.$acl_id.'">'.$acl_name.'</option>';									
								
									$n++;
								}
								
							echo '</select>';
						echo '</td>';
						echo '<script>';
						echo '$("#'.$name.'_acl").kendoDropDownList();';
						echo '</script>';				
					$i++;
				}
				?>
			<tr><td colspan="2" align="right"><br /><input type="submit" name="submit" value="Save Changes" class="k-button" /></td></tr>
		</table>
		</form>	
	</div>

</div>

<script>
// bind form using ajaxForm 
$('#update_permisssions').ajaxForm({ 
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