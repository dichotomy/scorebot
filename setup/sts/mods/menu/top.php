<?php if(isset($_SESSION['user_id'])) { ?>
<div id="top_menu">
<h1 class="application_name"><a href="?p=dashboard"><?php echo $application_title; ?></a></h1>
<div class="menu_left">
<ul id="nav_left">
<?php
$p_sql = "SELECT * FROM mods WHERE type = '1' AND parent = 'none' AND acl <= '$_SESSION[user_acl]' AND enabled = '1' AND name != 'end_user' ORDER BY weight";
$p_result = mysql_query($p_sql);
$p_num = mysql_num_rows($p_result);
$p_i = 0;

while ($p_i < $p_num) {

	$name = mysql_result($p_result, $p_i, "name");
	$display = mysql_result($p_result, $p_i, "display");
	$path = mysql_result($p_result, $p_i, "path");
	$acl = mysql_result($p_result, $p_i, "acl");
	
	
	$ck_sql = "SELECT * FROM mods WHERE parent = '$name' AND type = '1' AND acl <= '$_SESSION[user_acl]' AND enabled = '1' ORDER BY weight";
	$ck_result = mysql_query($ck_sql);
	$ck_num = mysql_num_rows($ck_result);
	$ck_i = 0;
	
	if($ck_num >= 1) {
		
		echo '<li><a href="#"><strong>'.$display.'</strong></a><ul>';
		
		while ($ck_i < $ck_num) {
		
			$c_name = mysql_result($ck_result, $ck_i, "name");
			$c_acl = mysql_result($ck_result, $ck_i, "icon");
			$c_display = mysql_result($ck_result, $ck_i, "display");
			$c_path = mysql_result($ck_result, $ck_i, "path");
			$c_icon = mysql_result($ck_result, $ck_i, "icon");
			$c_has_icon = mysql_result($ck_result, $ck_i, "has_icon");
		
			if($c_has_icon == 1) {
			
				echo '<li class="icon '.$c_icon.'"><a href="?p='.$c_name.'">'.$c_display.'</a></li>';
			
			} else {
			
				echo '<li><a href="?p='.$c_name.'">'.$c_display.'</a></li>';
				
			}
		
			$ck_i++;
		}
		
		echo '</ul></li>';
		
	} else {
		echo '<li><a href="?p='.$name.'"><strong>'.$display.'</strong></a></li>';
	}
	$p_i++;
}
?>

</ul>
</div>
<ul id="nav_right">
<li class="asdf">
    <a href="#"><strong><?php echo $_SESSION['ln'].', '.$_SESSION['fn']; ?></strong></a>
    <ul>
        <li class="icon options"><a href="?p=user_options">Options</a></li>
        <li class="icon logout"><a href="?p=logoff">Log Out</a></li>
    </ul>
</li>
</ul>
</div>
<div class="clear"></div>

<?php } ?>

