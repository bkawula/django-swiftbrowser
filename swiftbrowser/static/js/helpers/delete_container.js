//Bind the cancel button to the modal closing delete container modal
$('.cancel-delete').on('click', function() {
    $('#delete-container').foundation('reveal', 'close');
});

/*
    Disable the delete container form from submitting. Form to be re-enabled
	when the user confirms by typing in the container name.
*/
$("form#delete-container-form").on('submit', function(e) {
	e.preventDefault();
});

$("input.enter-container-name").focus();

//Check user's input matches container name.
$("input.enter-container-name").keyup(delete_check);

/*
	Check that the user correctly typed in the name before allowing the user
	to submit the delete form.
*/
function delete_check() {

    var user_input = $("input.enter-container-name").val();
    var container_name = $("form#delete-container-form span.container-name-holder").html();

    //Check to see if the user correctly typed in the name.
    if (user_input == container_name) {

        /* Display the form's submit button. The user is now able to submit
        the form.*/
        $(".confirm-delete").slideDown();

        /* Show the loader. */
        $("form#delete-container-form").on('submit', function() {
            $(".confirm-delete").hide();
            delete_container();
        });

        /* Stop the keyup checks. */
        $("input.enter-container-name").unbind("keyup");
    }
}

/*
    Make an asychrnonous call to the server to delete the container. Make
    additional calls to the server to update the progress bar.
*/
function delete_container() {

    //Display progress bar
    $(".css-progress-wrap").toggle(true);

    var formData = {
        csrfmiddlewaretoken  : $('input[name=csrfmiddlewaretoken]').val(),
        file_name            : "file_name",
    };

    $.ajax({
        type        : 'POST',
        url         : $("#delete-container-form").attr("data-delete-container-url"),
        data        : formData,
        dataType    : 'html',
        encode      : true,
        asych       : true,
    })

    .success(function (data) {
        // Close the modal, refresh the object table
        $('#delete-container').foundation('reveal', 'close');
        window.location.href=window.location.href;

    })

    .error(function(error) {
        console.log(error.responseText);
    });

    /* Recursively update the prorgess bar */
    update_progress_bar($("#container-total").attr("data-total-objects"));
}

/*
    Make a post to the server to get the remaining number of objects in the
    container.
*/
function update_progress_bar(total) {

    var formData = {
        csrfmiddlewaretoken  : $('input[name=csrfmiddlewaretoken]').val(),
    };

    $.ajax({
        type        : 'POST',
        url         : $("#delete-container-form").attr("data-container-count-url"),
        data        : formData,
        dataType    : 'html',
        encode      : true,
        asych       : false,
    })

    .success(function (data) {
        data = JSON.parse(data);
        var getPercent = 1 - (data.data.total/total);
        var getProgressWrapWidth = $('#css-progress-wrap').width();
        var progressTotal = getPercent * getProgressWrapWidth;
        var animationLength = 500;

        $('.css-progress-bar').stop().animate({
            left: progressTotal
        }, animationLength);
        if (getPercent !== 1) {
            update_progress_bar(total);
        }
    })

    .error(function(error) {
        console.log(error.responseText);
    });
}