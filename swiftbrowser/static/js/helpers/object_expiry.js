/*
	This file is loaded in object_expiry.html to handle the closing of the
	modal.
*/
$(function() {
	$("#close-object-expiry").on('click', function (){
        $('#object-expiry').foundation('reveal', 'close');
    });
});