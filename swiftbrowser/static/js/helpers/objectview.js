$( document ).ready(function() {
    loadTable();
});

function loadTable() {
    $('#objecttable').html(
        '<div id="progress" class="center-progress">' +
            '<div class="loader">Loading...</div>' +
        '</div>'
    );
    $("#progress").show();
    $.ajax({
        url: loadtable_url,
        success: function(data) {
            $('#objecttable').html(data);
            $(document).foundation();
            $(".alert-box").click(function(e){

                $(this).slideUp();
            });
        }
    }).fail( function(data) {
        //On error, refresh the page. This will redirect to login
        //if session is expired.
        location.reload();
    });
}

$('input[id=file]').change(function() {
    $('#filetmp').val($(this).val());
});

$('#create-pseudofolder').on('submit', function(event){
    event.preventDefault();
    $("#create-pseudofolder").hide();
    $("#progress").show();
    create_folder();

});

function addMessage(text, extra_tags) {
    if (extra_tags == 'success') {
        $("#messages").html(
            '<div data-alert class="alert-box success header-alert">' +
                '<div class="row" >' +
                    '<div class="small-12 columns">' +
                '<strong>Success.</strong> ' + text +
                '<a href="#" class="close">&times;</a>' +
                '</div>' +
                '</div>' +
            '</div>'
            );
    } else if (extra_tags == 'error') {
        $("#messages").html(
            '<div data-alert class="alert-box alert header-alert">' +
                '<div class="row" >' +
                    '<div class="small-12 columns">' +
                '<strong>Error.</strong> ' + text +
                '<a href="#" class="close">&times;</a>' +
                '</div>' +
                '</div>' +
            '</div>'
        );
    }
}

$(document).ready(function() {
    $('#messages').ajaxComplete(function(e, xhr, settings) {
        var contentType = xhr.getResponseHeader("Content-Type");

        if (contentType == "application/javascript" || contentType == "application/json") {
            var json = $.parseJSON(xhr.responseText);

            $.each(json.django_messages, function (i, item) {
                addMessage(item.message, item.extra_tags);
            });
        }
    }).ajaxError(function(e, xhr, settings, exception) {
        addMessage("There was an error processing your request, please try again.", "error");
    });
});


function create_folder() {
    $.ajax({
        method: "POST",
        url: create_folder_url,
        data: $('#create-pseudofolder').serialize()
    }).done(function() {
        $('#pseudoContainer').foundation('reveal', 'close');
        loadTable();
        $("#create-pseudofolder").show();
        $("#progress").hide();
    }).always(function(data, textStatus, jqXHR) {

        var contentType = jqXHR.getResponseHeader("Content-Type");

        if (contentType == "application/javascript" || contentType == "application/json") {
            var json = $.parseJSON(jqXHR.responseText);

            $.each(json.django_messages, function (i, item) {
                addMessage(item.message, item.extra_tags);
            });
        }
    });
};