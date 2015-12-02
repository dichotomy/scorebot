<?php
define('INCLUDE_CHECK',true);
include '../../../../config/connect.php';
$query = "SELECT * FROM categories WHERE id != '1' ORDER BY category";
$mysql_result = mysql_query($query);
$result = array();
while ($row = mysql_fetch_assoc($mysql_result)) {
   $result[] = $row;
}
$data = json_encode($result);

print_r($data);
?>