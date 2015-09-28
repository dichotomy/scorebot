<?php
if(isset($_SESSION['user_id'])) {

function dateDiff($start, $end) {

$diff = $start - $end;

return round($diff / 86400);

}

function timeDiff($time1, $time2) {
    $time1 = strtotime("1980-01-01 $time1");
    $time2 = strtotime("1980-01-01 $time2");
   if ($time2 < $time1) {
        $time2 += 86400;
    }    
  
    return date("H:i:s", strtotime("1980-01-01 00:00:00") + ($time2 - $time1));
}

function timeAdd($time1, $time2) {
    $time1 = strtotime("1980-01-01 $time1");
    $time2 = strtotime("1980-01-01 $time2");
   if ($time2 < $time1) {
        $time2 += 86400;
    }    
    
    return date("H:i:s", strtotime("1980-01-01 00:00:00") + ($time2 + $time1));
}

//GET TICKETS ASSIGNED TO CURRENT USER
$sql = "SELECT COUNT(*) AS count FROM tickets WHERE assigned_uid = '$_SESSION[user_id]' AND state_id = '1'";
$result = mysql_fetch_assoc(mysql_query($sql));
echo mysql_error();
$user_count = $result['count'];

//GET TICKETS OPEN ENTIRE SYSTEM
$sql = "SELECT COUNT(*) AS count FROM tickets WHERE  state_id = '1'";
$result = mysql_fetch_assoc(mysql_query($sql));
echo mysql_error();
$system_count = $result['count'];


//GET TICKETS ASSIGNED TO CURRENT GROUP
$sql = "SELECT COUNT(*) AS count FROM tickets WHERE assigned_gid = '$_SESSION[group_id]' AND state_id = '1'";
$result = mysql_fetch_assoc(mysql_query($sql));
echo mysql_error();
$group_count = $result['count'];

//GET TICKETS CLOSED BY USER TODAY
$sql = "SELECT COUNT(*) AS count FROM tickets WHERE resolved_uid = '$_SESSION[user_id]' AND state_id = '2' AND resolved_date = '$int_date'";
$result = mysql_fetch_assoc(mysql_query($sql));
echo mysql_error();
$user_closed_today = $result['count'];

//GET TICKETS CLOSED BY GROUP TODAY
$sql = "SELECT id FROM users WHERE group_id = '$_SESSION[group_id]'";
$result = mysql_query($sql);
$num = mysql_num_rows($result);
$i = 0;


while ($i < $num) {
	
	$user_id = mysql_result($result, $i, "id");
	$get = "SELECT COUNT(*) AS count FROM tickets WHERE resolved_uid = '$user_id' AND state_id = '2' AND resolved_date = '$int_date'";
	$result_get = mysql_fetch_assoc(mysql_query($get));
	echo mysql_error();
	$group_closed_today =+ $result_get['count'];
	$i++;
}

//GET USER AVERAGE RESOLUTION TIME
$sql = "SELECT * FROM tickets WHERE resolved_uid = '$_SESSION[user_id]' AND state_id = '2'";
$result = mysql_query($sql);
$num = mysql_num_rows($result);
$i = 0;
$r_total_time = date("00:00:00");
$times = array();
while ($i < $num) {

	$created_time = mysql_result($result, $i, "created_time");
	$created_date = mysql_result($result, $i, "created_date");
	$resolved_time = mysql_result($result, $i, "resolved_time");
	$resolved_date = mysql_result($result, $i, "resolved_date");

	$created_time = date('H:i:s', $created_time);
	$resolved_time = date('H:i:s', $resolved_time);	
	$hours = timeDiff($created_time, $resolved_time);
	
	$r_total_time = explode(":", $r_total_time );
	$a_hours = explode(":", $hours);
	
	$r_total_time = mktime($r_total_time[0], $r_total_time[1], $r_total_time[2]); 

	$r_total_time = date("H:i:s", strtotime("+" . $a_hours[0] . " hours +" . $a_hours[1] . " minutes +" . $a_hours[2] . " seconds", $r_total_time));
	
	
	$days = $days + dateDiff($resolved_date, $created_date);
	
 $i++;
}

	$r_total_time = explode(":", $r_total_time);
	
	$h = $r_total_time[0]/4;
	$m = $r_total_time[1]/4;
	$s = $r_total_time[2]/4;


	
	
	$user_days = $days.'d '.round($h).'h '.round($m).'m '.round($s).'s ';

//GET SYSTEM AVERAGE RESOLUTION TIME
$sql = "SELECT * FROM tickets WHERE state_id = '2'";
$result = mysql_query($sql);
$num = mysql_num_rows($result);
$i = 0;
$r_total_time = date("00:00:00");
$times = array();
while ($i < $num) {

	$created_time = mysql_result($result, $i, "created_time");
	$created_date = mysql_result($result, $i, "created_date");
	$resolved_time = mysql_result($result, $i, "resolved_time");
	$resolved_date = mysql_result($result, $i, "resolved_date");

	$created_time = date('H:i:s', $created_time);
	$resolved_time = date('H:i:s', $resolved_time);	
	$hours = timeDiff($created_time, $resolved_time);
	
	$r_total_time = explode(":", $r_total_time );
	$a_hours = explode(":", $hours);
	
	$r_total_time = mktime($r_total_time[0], $r_total_time[1], $r_total_time[2]); 

	$r_total_time = date("H:i:s", strtotime("+" . $a_hours[0] . " hours +" . $a_hours[1] . " minutes +" . $a_hours[2] . " seconds", $r_total_time));
	
	
	$days = $days + dateDiff($resolved_date, $created_date);
	
 $i++;
}

	$r_total_time = explode(":", $r_total_time);
	
	$h = $r_total_time[0]/4;
	$m = $r_total_time[1]/4;
	$s = $r_total_time[2]/4;


	
	
	$system_days = $days.'d '.round($h).'h '.round($m).'m '.round($s).'s ';

?>
<div class="section_960">
	<div class="section_125_l">
		<?php include 'dashboard_menu.php'; ?>
	</div>
	<div class="section_780_r">
		<div class="dashboard_item">
			<h2>Assigned</h2>
			<h1><?php echo $user_count; ?></h1>
			<h3>To You</h3>
		</div>
		<div class="dashboard_item">
			<h2>Assigned</h2>
			<h1><?php echo $group_count; ?></h1>
			<h3>To Group</h3>
		</div>
		<div class="dashboard_item">
			<h2>Closed by You</h2>
			<h1><?php echo $user_closed_today; ?></h1>
			<h3>This Year</h3>
		</div>
		<div class="dashboard_item">
			<h2>Closed by</h2>
			<h1><?php echo $user_closed_today; ?></h1>
			<h3>You Today</h3>
		</div>
		<div class="dashboard_item">
			<h2>Closed by</h2>
			<h1><?php echo $group_closed_today; ?></h1>
			<h3>Group Today</h3>
		</div>
		<div class="dashboard_item">
			<h2>Your Avgerage</h2>
			<h4><?php echo $user_days; ?></h4>
			<h3>Resolution Time</h3>
		</div>
	</div>
	<div class="clear"></div>
	<br />
	<div class="section_780_r">
		<div class="dashboard_item_no_float">
			<h2>Average Close Time</h2>
			<h1><?php echo $system_days; ?></h1>
			<h3>Entire System</h3>
		</div>

	</div>
	<div class="clear"></div>
	<br />
	<div class="section_780_r">
		<div class="dashboard_item_no_float">
			<h2>All Open Tickets</h2>
			<h1><?php echo $system_count; ?></h1>
			<h3>Entire System</h3>
		</div>

	</div>
</div>


<?php
}
?>