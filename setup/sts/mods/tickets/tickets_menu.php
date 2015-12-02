<?php if(isset($_SESSION['user_id'])) { ?>
	<table class="full">
		<tr><td><p><a href="#" id="create_ticket">Create Ticket</a></p></td>
	<?php
	$sql = "SELECT * FROM mods WHERE parent = 'tickets' AND type = '1' AND acl <= '$_SESSION[user_acl]' ORDER BY weight";
	$result = mysql_query($sql);
	$num = mysql_num_rows($result);
	$i = 0;
	while ($i < $num) {
	
		$name = mysql_result($result, $i, "name");
		$acl = mysql_result($result, $i, "acl");
		$display = mysql_result($result, $i, "display");
		
			echo '<td><p><a href="?p='.$name.'">'.$display.'</a></p></td>';
			
		$i++;
		
		
	}
	?>
	</tr>
	</table>
<?php } ?>