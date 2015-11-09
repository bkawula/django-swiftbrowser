$(document).foundation();

/*
	Focus on the text box when Create Container modal is opened.
*/
$(document).on('opened.fndtn.reveal', '#container[data-reveal]', function () {
    $("#create-container-name").first().focus();
});

/*
    Clear the create container textbox when modal is closed.
*/
$(document).on('closed.fndtn.reveal', '#container[data-reveal]', function () {
    $("#create-container-name").first().val("");
});

/*
	Focus on the text box when Delete Container modal is opened.
*/
$(document).on('opened.fndtn.reveal', '#delete-container[data-reveal]', function () {
    $("#delete-container-name").first().focus();

	//Hide the delete button
	$("#delete-container-submit").hide();
	//Clear the input
	$("input.enter-container-name").val("");
});

/*
	Clear the textbox when delete container modal is closed. Hide the confirmation button
*/
$(document).on('closed.fndtn.reveal', '#delete-container[data-reveal]', function () {
    $("#create-container-name").first().val("");
});

$('#create-container').on('submit', function(event) {
	// Hide the submit button.
	$("#create-container").hide();
	// Display the progress animation.
	$(".progress").show();
});

/*
	Disable the delete container form from submitting. Form to be re-enabled
	when the user confirms by typing in the container name.
*/
$("form#delete-container-form").on('submit', function(e) {
	e.preventDefault();
});

//Bind the cancel button to the modal closing delete container modal
$('#cancel-delete').on('click', function() {
	$('#delete-container').foundation('reveal', 'close');
});

//Populate delete form with necessary information.
$(".delete-container-link").on('click', function() {
	var delete_link = $(this).attr("data-url");
	var container_name = $(this).attr("data-container-name");
	$("form#delete-container-form").attr("action", delete_link);
	$("form#delete-container-form span.container-name-holder").html(container_name);
});

//Check user's input matches container name.
$("input.enter-container-name").keyup(delete_container_check);

/*
	Check that the user correctly typed in the container name on delete.
*/
function delete_container_check() {
	var user_input = $("input.enter-container-name").val();
	var container_name = $("form#delete-container-form span.container-name-holder").html();
	if (user_input == container_name) {
		$("#delete-container-submit").slideDown();

		/*Enable the form. */
		$("form#delete-container-form").unbind("submit");

		/* Show the loader*/
		$("form#delete-container-form").on('submit', function() {
			$("#delete-container-submit").hide();
			$("#cancel-delete").hide();
			$(".progress").show();
		});

		/* Stop the keyup checks. */
		$("input.enter-container-name").unbind("keyup");

		return true;
	} else {
		$("#delete-container-submit").hide();
		return false;
	}
}

/*
	Edit ACLs: cancel button
*/
$('#cancel-edit-access').on('click', function() {
	$('#edit-acl').foundation('reveal', 'close');
});

/*
	Attach event to set container name for angular app
*/
$("a.edit-acl").on('click', function() {
	var container_name = $(this).attr("data-container-name");
    angular.element("#edit-acl").scope().setContainerName(container_name);
});
