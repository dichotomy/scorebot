<?php
if(isset($_SESSION['user_id'])) {
?>
<div class="eu_portal_wrapper">
	<div id="server_message">
		<div class="info">
			Please explain the issue you are having below.
		</div>
	</div>
	<form name="create_ticket" id="create_ticket" method="post" action="?p=process_eu_ticket">
	<table class="full">
		<tr><th align="left">Subject</th></tr>
		<tr><td><input type="text" name="subject" id="subject" class="k-textbox full" /></td></tr>
		<tr><th align="left">Issue</th></tr>
		<tr><td><textarea name="issue" id="issue" class="k-textbox full"></textarea></td></tr>
		<tr><td align="right"><input type="submit" name="submit" value="Submit Ticket!" class="k-button"></td></tr>
	</table>
	</form>
</div>

<script>
$("#issue").kendoEditor({
	encoded: false
});
$('#create_ticket').ajaxForm({ 
	// target identifies the element(s) to update with the server response 
    target: '#server_message', 
 
    // success identifies the function to invoke when the server response 
    // has been received; here we apply a fade-in effect to the new content 
    success: function() { 
    $('#server_message').fadeIn("slow"); 
            
    } 
});
</script>
<?php
}
?>

