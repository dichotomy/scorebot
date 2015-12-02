<?php if(isset($_SESSION['user_id'])) { ?>

<div class="section_960">
		
    	<div id="category_window"></div>
	<div class="section_300_l" id="gridWrapper">

		<div id="categories_grid"></div>
	</div>
	<div class="section_600_r">
		<div id="tabStrip">
    		<ul>
     		   <li>Information</li>
   		 </ul>
    	<div>
    		<div class="info">
    			Double click a ticket from the list to the left to open it here.
    		</div>
    	</div>
	</div>		
	</div>
	<div class="clear"></div>
<div class="section_960_b">
<?php include('tickets_menu.php'); ?>
</div>
</div>	
	


<script>
$("#tabStrip").kendoTabStrip({
	//contentUrls: ["?p=create_ticket"]
});

var tabstrip = $("#tabStrip").data("kendoTabStrip");
tabstrip.select(tabstrip.tabGroup.children("li:first"));

function closetab () {
	var tab = tabstrip.select(),
    otherTab = tab.next();
    otherTab = otherTab.length ? otherTab : tab.prev();

    tabstrip.remove(tab);
    tabstrip.select(otherTab);
	//openItems = openItems - 1;
	createGrid();
};



var openItems = 0;


function createGrid() {

	$('#gridWrapper').empty().html('<div id="categories_grid"></div>')
	var grid = $("#categories_grid").kendoGrid({
    	dataSource: {
    		transport: {
        		read: {
            		url: "mods/tickets/data/get_all_tickets_assigned_to_user.php?id=<?php echo $_SESSION['user_id']; ?>",
            		dataType: "json"
        		}
    		},
            schema: {
            	model: {
            		id: "id",
                	fields: {
                    	id: { type: "number" },
	                    subject: { type: "string" },
	                    name: { type: "string" },
	                    mail: { type: "string" },
	                    category: { type: "string" },
	                    state_name: { type: "string" },
	                    
	                    
                	}
                }
            },
            pageSize: 40
            },
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
            	title:"Assigned To You",
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



    

</script>
<style>
.asdf{
margin-left:10000px;
float:right;
}
</style>
<?php } ?>