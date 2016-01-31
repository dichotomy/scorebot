<?php
if(isset($_SESSION['user_id'])) { 

	$sql = "SELECT mods.name, mods.display, mods.parent, acls.id, acls.name FROM "
	."mods, acls WHERE mods.acl = acls.id AND type != '3' ORDER BY mods.name";
	$result = mysql_query($sql);
	echo mysql_error();
	$num = mysql_num_rows($result);
	$i = 0;	
	
	while ($i < $num) {
	
		$name = mysql_result($result, $i, "name");
		$display = mysql_result($result, $i, "display");
		$c_acl_id = mysql_result($result, $i, "acls.id");
		$c_acl_name = mysql_result($result, $i, "acls.name");
		$parent = mysql_result($result, $i, "parent");
		
		$acl_update = $name.'_acl';
		$acl_update = $_POST[''.$acl_update.''];
		
		$update = "UPDATE mods SET acl = '$acl_update' WHERE name = '$name'";
		mysql_query($update);
		
		if($parent != "none") {
			
			$update_child = "UPDATE mods SET acl='$acl_update' WHERE parent='$name'";
			mysql_query($update_child);

		}
				
		$i++;
	}

} 


?>