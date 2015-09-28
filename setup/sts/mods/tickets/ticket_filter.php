<?php
if(isset($_SESSION['user_id'])) {
?>
	<table class="full">
		<tr>
		<td align="right">ID:</td><td><input type="number" name="id" id="id" class="k-textbox full" onChange="filter()" /></td>
			<td align="right">Location:</td>
			<td>
					<select name="location_id" id="location_id" class="full" onChange="filter()">
						<option value="null"></option>
						<?php
						$sql = "SELECT * FROM locations WHERE type = '1' ORDER BY name";
						$result = mysql_query($sql);
						echo mysql_error();
						$num = mysql_num_rows($result);
						$i = 0;
						while ($i < $num) {
							
							$id = mysql_result($result, $i, "id");
							$name = mysql_result($result, $i, "name");
								
							echo '<option value='.$id.'>'.$name.'</option>';
							
							$i++;
						}
						?>
					</select>
			</td>
		</tr>
	</table>
<?php
}
?>