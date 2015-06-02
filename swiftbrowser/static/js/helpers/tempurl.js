/* This is a helper file for tasks completed in tempurls. */

$(function() {
	//Close tempurl modal
	$('#close-tempurl').on('click', function(){$('#tempurl').foundation('reveal', 'close')});

	//Select the tempurl on modal open.
	$(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
		$("#generated-tempurl").select();

		console.log($("#generated-tempurl"));

		//Select the tempurl on icon click.
		$("#highlight-icon").on("click", function() {
			$("#generated-tempurl").select();
		});
	});



	/* Ajax for custom temp url form submission. */
});