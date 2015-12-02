<?php if(isset($_SESSION['user_id'])) { ?>

<div class="section_960">
 	<div id="category_window"></div>
	<div class="section_300_l">
		<h1>Search Tickets</h1>
		
		<br />
		<table class="full">
			<tr><td align="left">Ticket ID</td></tr>
			<tr><td><input type="text" name="id" id="id" class="k-textbox full" /></td></tr>
			<tr><td align="left">End User</td></tr>
			<tr>
				<td width="280">
					<select name="eu_id" id="eu_id" class="full" >
						<option value="null"></option>
						<?php
						$sql = "SELECT id, mail FROM users ORDER BY mail";
						$result = mysql_query($sql);
						echo mysql_error();
						$num = mysql_num_rows($result);
						$i = 0;
						while ($i < $num) {
						
							$id = mysql_result($result, $i, "id");
							$mail = mysql_result($result, $i, "mail");
								
							echo '<option value='.$id.'>'.$mail.'</option>';
							
							$i++;
						}
						?>
					</select>
				</td>
			</tr>
			
			<tr><td align="left">Location</td></tr>
			<tr>
				<td width="280">
					<select name="location_id" id="location_id" class="full" >
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
			<tr><td align="left">Category</td></tr>
			<tr>
				<td>
					<select name="category_id" id="category_id" class="full">
						<option value="null"></option>
						<?php
						$sql = "SELECT * FROM categories ORDER BY category";
						$result = mysql_query($sql);
						echo mysql_error();
						$num = mysql_num_rows($result);
						$i = 0;
						while ($i < $num) {
							
							$id = mysql_result($result, $i, "id");
							$category = mysql_result($result, $i, "category");
							
							echo '<option value='.$id.'>'.$category.'</option>';
							
							$i++;
						}
						?>
					</select>
				</td>
			</tr>
			<tr>
			<tr><td align="right"><button name="clear_filter" class="k-button full" onClick="clear_filter()">Clear Results</button> <button name="print_results" class="k-button full" onClick="clear_filter()">Print Results</button> <button name="filter" class="k-button full" onClick="filter()">Search</button></td></tr>
		</table>	
	</div>
	<div class="section_600_r" id="gridWrapper">
		<div id="categories_grid"></div>
	</div>		
	</div>
	<div class="clear"></div>
<div class="section_960_b">
<?php include('tickets_menu.php'); ?>
</div>
</div>	
	


<script>
var shawn = 0;
var ticketDataSource = new kendo.data.DataSource ({
    transport: {
        read: {
            url: "mods/tickets/data/get_all_tickets.php",
            dataType: "json"
        }
    },
	schema: {
    	model: {
        	id: "id",
            fields: {
            	id: { type: "string" },
	            subject: { type: "string" },
	            name: { type: "string" },
	            mail: { type: "string" },
	            category: { type: "string" },
	            state_name: { type: "string" },
	            eu_id: { type: "string" },
	            location_id: { type: "string" },
	            category_id: { type: "string" },
	            group_id: { type: "string" },
	            assigned_uid: { type: "string" },
            }
        }
    }
});

function createGrid() {

	$('#gridWrapper').empty().html('<div id="categories_grid"></div>')
	var grid = $("#categories_grid").kendoGrid({
    	dataSource:	ticketDataSource,
            height: 700,
            filterable: true,
            sortable: true,
            pageable: false,
            selectable:true,
            scrollable: {
            	virtual:true,
            },
            change: function (e) {
            
            	var selectedItem = this.dataSource.view()[this.select().index()];
            	selectedTicketID = (selectedItem.id);
            	
            	
            	
            	tabeText = "Ticket#:" + selectedTicketID + " [<span onclick='closetab()'>X</span>]";
            	tabUrl = "?p=edit_ticket&id=" +selectedTicketID;
            
            },
            columns: [{
            	title:"Assigned To Group",
            	field: "subject",
                template: '<p class="ticket_id"><em>#=mail#</em></p><p class="ticket_category">#=category#</p><div class="clear"></div><p class="ticket_issue"><strong>#=subject#</strong></p><p class="ticket_eu">#=name#</p><p class="ticket_state">#=state_name#</p>',
            }],
            
            
    		
    }).data("kendoGrid");

	$("#categories_grid").dblclick(function(){
		openItems = openItems + 1;
   		tabstrip.append([
   			{
   				text: tabeText,
   				contentUrl: tabUrl,
   				encoded: false
   				
   			}
   		]);
   		tabstrip.select(openItems);
   		//alert(openItems);
 	});

}

 	$("#create_ticket").click(function(){
	var window = $("#category_window");
 	if (!window.data("kendoWindow")) {
        // window not yet initialized
        window.kendoWindow({
       height: "200px",
        title: "<?php echo $application_title; ?>",
        visible: false,
        width: "600px",
        height: "600px",
        modal: true,
        draggable: false,
        close: onClose,
        });
        // reopening window
        window.data("kendoWindow")
        	.center()
            .content("Loading...") // add loading message
            .refresh("<?php echo $application_root; ?>?p=create_ticket")
            .open(); // open the window        

    } else {
        // reopening window
        window.data("kendoWindow")
        	.center()
            .content("Loading...") // add loading message
            .refresh("<?php echo $application_root; ?>?p=create_ticket")
            .open(); // open the window
    }	

		
 	});

var tabstrip = $("#tabStrip").data("kendoTabStrip");

 	createGrid();
 	
 	$("#refresh").click(function() {
 	
 		createGrid();
 	
 	});
 	
	function onClose() {

		createGrid();

	};
	
	function filter_id(changeVal) {
			var value = changeVal.value;
			//alert(value);
	        ticketDataSource .filter({
            field: "id",
            operator: "eq",
            value: value
        });
	};
	
	function filter_subject(changeVal) {
			var value = changeVal.value;
			//alert(value);
	        ticketDataSource .filter({
            field: "subject",
            operator: "contains",
            value: value
        });
	};
	
	function clear_filter() {
		ticketDataSource .filter({});
	}
	
		
	function filter() {
		ticketDataSource.filter({
			logic: "or",
			filters: [
				{field: "id", operator: "eq", value: $("#id").val()},
				{field: "eu_id", operator: "eq", value: $("#eu_id").val()},
				{field: "location_id", operator: "eq", value: $("#location_id").val()},
				{field: "category_id", operator: "eq", value: $("#category_id").val()},
			]
		});	
		
	};

$("#eu_id").width("100%").kendoComboBox();
$("#category_id").width("100%").kendoComboBox();
$("#location_id").width("100%").kendoComboBox();
$("#group").width("100%").kendoComboBox();
$("#assigned_uid").width("100%").kendoComboBox();



    

</script>
<?php } ?>