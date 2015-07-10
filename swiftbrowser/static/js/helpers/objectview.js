$( document ).ready(function() {
    //loadTable();
});

/*
    After a table is loaded, new events need to be applied to the page.
*/
function applyTableEvents() {

    //Re-apply foundation
    $(document).foundation();

    //Reapply dismiss of alert boxes
    $(".alert-box").click(function(e){
        $(this).slideUp();
    });

    //Delete object binding.
    $("a.delete-object").on("click",function(e) {
        //Prompt user to confirm.
        if (confirm("Are you sure you want to delete " + $(this).attr("data-name") + "?")) {
            showLoader();
            $("#progress").show();
        } else {
            e.preventDefault();
        }
    });

    //Delete folder binding.
    $("a.delete-folder").on("click", function(e) {

        if (confirm("Are you sure you want to delete " + $(this).attr("data-name") + "?")) {
            if (confirm("This will delete " + $(this).attr("data-name")+" and all it's contents. Are you sure?")) {
                showLoader();
                $("#progress").show();
            } else {
                e.preventDefault();
            }
        } else {
            e.preventDefault();
        }
    });

}
/*
    Display the loader in the object table.
*/
function showLoader() {

    $('#objecttable').html(
        '<div id="progress" class="center-progress">' +
            '<div class="loader">Loading...</div>' +
        '</div>'
    );
}


function double_confirm() {
    var confirm1 = confirm('Delete folder?');
    if (confirm1) {
        var confirm2 = confirm('Deleting this folder will delete everything in the folder. Are you sure?');
        if (confirm2) {
            return true;
        } else {
            return false;
        }
    } else {
        return false;
    }
}

// function loadTable() {
//     showLoader();
//     $("#progress").show();
//     $.ajax({
//         url: loadtable_url,
//         success: function(data) {
//             $('#objecttable').html(data);
//             applyTableEvents();
//         }
//     }).fail( function(data) {
//         //On error, refresh the page. This will redirect to login
//         //if session is expired.
//         location.reload();
//     });
// }

function create_folder() {
  /*global create_folder_url: true*/
  /*jslint unparam: true*/
  $.ajax({
    method: "POST",
    url: create_folder_url,
    data: $('#create-pseudofolder').serialize()
  })
    .always(function (data, textStatus, jqXHR) {

      loadTable();
      $('#pseudoContainer').foundation('reveal', 'close');
      $("#create-pseudofolder").show();
      $("#pseudoContainer #progress").hide();
      $("input#foldername").val("");
      var contentType = jqXHR.getResponseHeader("Content-Type");

      if (contentType === "application/javascript" || contentType === "application/json") {
        var json = $.parseJSON(jqXHR.responseText);

        $.each(json.django_messages, function (i, item) {
          /* jshint unused:vars */
          addMessage(item.message, item.extra_tags);
        });
      }
    });
  /*jslint unparam: false*/
}

$(document).ready(function () {
  //loadTable();
});


$(document).ready(function () {
  /*jslint unparam: true*/
  $('#messages').ajaxComplete(function (e, xhr, settings) {
    var contentType = xhr.getResponseHeader("Content-Type");

    if (contentType === "application/javascript" || contentType === "application/json") {
      var json = $.parseJSON(xhr.responseText);

      $.each(json.django_messages, function (i, item) {
        addMessage(item.message, item.extra_tags);
      });
    }
  })
    .ajaxError(function () {
      addMessage("There was an error processing your request, please try again.", "error");
    });
  /*jslint unparam: false*/
});

// $('#create-pseudofolder').on('submit', function(event){
//     event.preventDefault();
//     $("#create-pseudofolder").hide();
//     $("#progress").show();
//     create_folder();

// });

// function create_folder() {
//     $.ajax({
//         method: "POST",
//         url: create_folder_url,
//         data: $('#create-pseudofolder').serialize()
//     }).done(function() {
//         $('#pseudoContainer').foundation('reveal', 'close');
//         loadTable();
//         $("#create-pseudofolder").show();
//         $("#progress").hide();
//     }).always(function(data, textStatus, jqXHR) {

//         var contentType = jqXHR.getResponseHeader("Content-Type");

//         if (contentType == "application/javascript" || contentType == "application/json") {
//             var json = $.parseJSON(jqXHR.responseText);

//             $.each(json.django_messages, function (i, item) {
//                 addMessage(item.message, item.extra_tags);
//             });
//         }
//     });
// };

