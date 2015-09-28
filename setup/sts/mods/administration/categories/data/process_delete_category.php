<?php
if(isset($_SESSION['user_id'])) {

	$sql = "DELETE FROM categories WHERE id = '$_GET[id]'";
	mysql_query($sql);
	echo mysql_error();
	
	
	echo '<div class="success">';
	echo 'The category has been deleted.';
	echo '</div>';

}
?>