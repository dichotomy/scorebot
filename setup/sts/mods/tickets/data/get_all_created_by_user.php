<?php
define('INCLUDE_CHECK',true);
include '../../../config/connect.php';

$user_id = $_GET['id'];

$query = "SELECT tickets.id, tickets.subject, locations.name, users.mail, categories.category, "
."created_date,created_time, tickets.state_id, states.name AS state_name FROM tickets, locations, "
."users, categories, states WHERE tickets.location_id = locations.id AND tickets.eu_uid = users.id "
."AND tickets.category_id = categories.id AND tickets.state_id = states.id AND state_id != '0' AND created_uid ='$user_id' ORDER BY tickets.id DESC";
$mysql_result = mysql_query($query);
echo mysql_error();
$result = array();
while ($row = mysql_fetch_assoc($mysql_result)) {
   $result[] = $row;
}
$data = json_encode($result);

print_r($data);
?>