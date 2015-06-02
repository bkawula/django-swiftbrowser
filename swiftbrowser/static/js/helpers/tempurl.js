/* This is a helper file for tasks completed in tempurls. */

$(function() {
	//Close tempurl modal
	$('#close-tempurl').on('click', function(){$('#tempurl').foundation('reveal', 'close')});

	//Select the tempurl on page load.
	$("#tempurl").select();

	//Select the tempurl on icon click.
	$("#highlight-icon").on("click", function() {
		$("#tempurl").select();
	});
});