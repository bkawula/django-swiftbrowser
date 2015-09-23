function loadTable() {
  $('#objecttable').html(
    '<div id="progress" class="center-progress">' +
      '<div class="loader">Loading...</div>' +
      '</div>'
  );
  $("#progress").show();
  /*global loadtable_url: true*/
  $.ajax({
    url: loadtable_url,
    success: function (data) {
      $('#objecttable').html(data);
      $(document).foundation();
      $(".alert-box").click(function () {
        $(this).slideUp();
      });
    }
  }).fail(function () {
    /*global location: true*/
    //On error, refresh the page. This will redirect to login
    //if session is expired.
    location.reload();
  });
}

function addMessage(text, extra_tags) {
  if (extra_tags === 'success') {
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
  } else if (extra_tags === 'error') {
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
  loadTable();
});

$('input[id=file]').change(function () {
  $('#filetmp').val($(this).val());
});

$('#create-pseudofolder').on('submit', function (event) {
  event.preventDefault();
  $("#create-pseudofolder").hide();
  $("#pseudoContainer #progress").show();
  create_folder();
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
