$(document).foundation();

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
