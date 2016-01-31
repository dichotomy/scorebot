<?php
if(isset($_SESSION['user_id'])) {

	$sql = "DELETE FROM locations WHERE id = '$_GET[id]'";
	mysql_query($sql);
	echo mysql_error();
	
	
	echo '<div class="success">';
	echo 'The location has been deleted.';
	echo '</div>';

}
?>