<?php
define('INCLUDE_CHECK',true);
include '../../../config/connect.php';
$query = "SELECT tickets.id, tickets.subject, locations.name, locations.id AS location_id, users.mail, users.id AS eu_id, categories.category, "
."created_date,created_time, tickets.state_id, states.name AS state_name, "
."tickets.category_id AS category_id, tickets.assigned_gid AS group_id, tickets.assigned_uid AS assigned_uid FROM tickets, locations, "
."users, categories, states WHERE tickets.location_id = locations.id AND tickets.eu_uid = users.id "
."AND tickets.category_id = categories.id AND tickets.state_id = states.id ORDER BY tickets.id DESC";
$mysql_result = mysql_query($query);
echo mysql_error();
$result = array();
while ($row = mysql_fetch_assoc($mysql_result)) {
   $result[] = $row;
}
$data = json_encode($result);

print_r($data);
?>