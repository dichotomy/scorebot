<?php if(isset($_SESSION['user_id'])) { ?>
<div class="section_960">

	<div class="section_125_l">
		<?php include 'locations_menu.php'; ?>
	</div>
	
	<div class="section_780_r" id="gridWrapper">
		<div id="category_window"></div>
	
		<div id="categories_grid"></div>
		
	</div>
</div>

<script>
$(document).ready(function(){
    var window = $("#category_window").kendoWindow({
        height: "200px",
        title: "<?php echo $application_title; ?>",
        visible: false,
        width: "780px",
        height: "150px",
        modal: true,
        draggable: false,
        close: onClose,
        //close: onClose(),
       
    }).data("kendoWindow");
    var window = $("#category_window").kendoWindow({
        height: "200px",
        title: "<?php echo $application_title; ?>",
        visible: false,
        width: "780px",
        height: "150px",
        modal: true,
        draggable: false,
        close: onClose(),
    }).data("kendoWindow");
    


function createGrid() {
	$('#gridWrapper').empty().html('<div id="categories_grid"></div>')
	var grid = $("#categories_grid").kendoGrid({
    	dataSource: {
    		transport: {
        		read: {
            		url: "mods/administration/locations/data/get_all_locations.php",
            		dataType: "json"
        		}
    		},
            schema: {
            	model: {
            		id: "id",
                	fields: {
                    	id: { type: "number" },
	                    name: { type: "string" },
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
            	selectedCategoryID = (selectedItem.id);
            	
            	//onChange();
            
            },
            columns: [{
            	title:"Double click a location to modify.",
                field:"name"  
            }],
            
            
    		
    }).data("kendoGrid");

	$("#categories_grid").dblclick(function(){
   		var window = $("#category_window");
 	if (!window.data("kendoWindow")) {
        // window not yet initialized
        window.kendoWindow({
       height: "200px",
        title: "<?php echo $application_title; ?>",
        visible: false,
        width: "780px",
        height: "125px",
        modal: true,
        draggable: false,
        close: onClose,
        });
        // reopening window
        window.data("kendoWindow")
        	.center()
            .content("Loading...") // add loading message
            .refresh({
            	url: "?p=edit_location",
            	data: { id: selectedCategoryID },
            })
            .open(); // open the window        

    } else {
        // reopening window
        window.data("kendoWindow")
        	.center()
            .content("Loading...") // add loading message
            .refresh({
            	url: "?p=edit_location",
            	data: { id: selectedCategoryID },
            })
            .open(); // open the window
    }

 	});

}
	


 	$("#add_location").click(function(){
	var window = $("#category_window");
 	if (!window.data("kendoWindow")) {
        // window not yet initialized
        window.kendoWindow({
       height: "200px",
        title: "<?php echo $application_title; ?>",
        visible: false,
        width: "780px",
        height: "125px",
        modal: true,
        draggable: false,
        close: onClose,
        });
        // reopening window
        window.data("kendoWindow")
        	.center()
            .content("Loading...") // add loading message
            .refresh("<?php echo $application_root; ?>?p=add_location")
            .open(); // open the window        

    } else {
        // reopening window
        window.data("kendoWindow")
        	.center()
            .content("Loading...") // add loading message
            .refresh("<?php echo $application_root; ?>?p=add_location")
            .open(); // open the window
    }	

		
 	});
 	
 	createGrid();
 	
 	$("#refresh").click(function() {
 	
 		createGrid();
 	
 	});
 	
	function onClose() {

		createGrid();

	};



    
});
</script>
<?php } ?>