<?php if(isset($_SESSION['user_id'])) { ?>
<?php

	//GET USER TO EDIT
	
	$id = $_GET['id'];


?>

	<div class="section_780">
		<div id="tabStrip">
		    <ul>
        		<li class="k-state-active">User Details</li>
		        <li>Reset Password</li>
		    </ul>
	    	<div></div>
	    	<div></div>
		</div>
	</div>


<script>
$("#tabStrip").kendoTabStrip({
	contentUrls: ["?p=user_details&id=<?php echo $id; ?>", "?p=reset_user_password&id=<?php echo $id; ?>"]
});
// bind form using ajaxForm 
$('#edit_category').ajaxForm({ 
	// target identifies the element(s) to update with the server response 
    target: '#server_message', 
 
    // success identifies the function to invoke when the server response 
    // has been received; here we apply a fade-in effect to the new content 
    success: function() { 
    $('#server_message').fadeIn("slow"); 
            
    } 
});

$('#delete_category').ajaxForm({ 
	// target identifies the element(s) to update with the server response 
    target: '#server_message', 
 
    // success identifies the function to invoke when the server response 
    // has been received; here we apply a fade-in effect to the new content 
    success: function() { 
    $('#server_message').fadeIn("slow"); 
            
    } 
});
</script>

<?php } ?>