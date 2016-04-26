/*
  This file helps manage the file uploading process in upload_form.html
*/
var files_added = 0; /* Track files added to the upload. */
var files_processed = 0; /* Track files that are processed.*/
var files_uploaded = 0; /* Track successful uploads. */

function closeForm() {
  $('#fileForm').foundation(
    {reveal: {close_on_background_click: true, close_on_esc: true}}
  );

  setTimeout(function () {
    $('#fileForm').foundation('reveal', 'close');
    setTimeout(function () {
      $('#preloadmsg').show();
      $('.fileupload-progress').hide();
      $('#start-upload').addClass('disabled');
      $('#cancel-upload').addClass('disabled');
      $('#close-upload').on('click', function () {
        $('#fileForm').foundation('reveal', 'close');
      }).removeClass('disabled');
    }, 500);
  }, 250);

  //Display error if any uploads fail
  var failed_count = files_added - files_uploaded;
  if (failed_count) {
    var failure_message = "Failed to upload " + failed_count;
    if (failed_count === 1) {
      failure_message += " file.";
    } else {
      failure_message += " files.";
    }
    angular.element("#objecttable").scope().MessagesHandler.newErrorMessage(failure_message);
  } else {
    var success_message;
    if (files_uploaded === 1) {
      success_message = "Successfully uploaded 1 file.";
    } else {
      success_message = "Successfully uploaded " + files_uploaded + " files.";
    }
    angular.element("#objecttable").scope().MessagesHandler.newSuccessMessage(success_message);
  }

  /* Reset the counters */
  files_uploaded = 0;
  files_added = 0;
  files_processed = 0;
}

/* Bind close button on the upload form. */
$('#close-upload').on('click', function () {
  $('#fileForm').foundation('reveal', 'close');
});

$(function () {
  'use strict';

  /*
      Initialize the jQuery File Upload widget.
  */

  var formData = $('#fileupload').serializeArray();
  formData.push(
    {name: "redirect", value: ""}
  );

  $('#fileupload').fileupload({
    formData: formData,
    url: $(this).attr('action'),
    method: 'POST',
    dataType: 'text',
    sequentialUploads: true,
    recalculateProgress: false,
    previewMaxWidth: 100,
    previewMaxHeight: 100,
    maxFileSize: $('#fileupload input[name=max_file_size]').val()
  })

    // Keep a counter of files as they are added.
    .bind('fileuploadadd', function () {
      files_added += 1;
      if ($('#fileForm').hasClass('open') === false) {
        $('#fileForm').foundation('reveal', 'open');
      }
    })

    //Called on successful file upload
    .bind('fileuploaddone', function () {
      files_uploaded += 1;
    })

    //Called when upload starts
    .bind('fileuploadprocessstart', function () {
      $('#preloadmsg').hide();
      $('.fileupload-progress').show();
      $('#start-upload').removeClass('disabled');
      $('#cancel-upload').removeClass('disabled');
    })

    //Called when an individual upload has finished
    .bind('fileuploadprocessdone', function () {
      if (files_added > 1) {
        $('.file-progress').show();
      }
    })

    .bind('fileuploadsend', function (e, data) {
      Foundation.libs.reveal.settings.close_on_background_click = false;
      $('#close-upload').off().addClass('disabled');
      $.each(data.files, function () {
        $('#fileForm').foundation(
          {
            reveal: {close_on_background_click: false, close_on_esc: false}
          }
        );
      });
    })

    // This is called when an item in the form is cancelled, files removed and
    // when files fail.
    .bind('fileuploadfail', function (e, data) {
      if (data.errorThrown === "abort") {
        files_added -= 1;
      }
      if (files_added === 0) {
        $('#preloadmsg').show();
        $('.fileupload-progress').hide();
      }
    })

    // Keep a counter of files as they are processed.
    .bind('fileuploadalways', function () {
      files_processed += 1;

      // If all files have been processed, close the form.
      if (files_processed === files_added) {
        closeForm();
        angular.element("#objecttable").scope().refreshObjectTable();
        files_added = 0;
        files_processed = 0;
        files_uploaded = 0;
        $(".crumb-row.fixed").remove();
      }
    })

    .addClass('fileupload-processing');
});

/*
  Bind events for cancelling an upload.
*/
$('#cancel-upload').click(function () {
  $('#fileForm').foundation(
    {reveal: {close_on_background_click: true, close_on_esc: true}}
  );
  $('#preloadmsg').show();
  $('.fileupload-progress').hide();

  //Reset the counters
  files_uploaded = 0;
  files_added = 0;
  files_processed = 0;

  $('#start-upload').addClass('disabled');
  $('#cancel-upload').addClass('disabled');
  $('#close-upload').on('click', function () {
    $('#fileForm').foundation('reveal', 'close');
  }).removeClass('disabled');
});

//Add a special class for chrome
if (navigator.userAgent.toLowerCase().match('chrome')) {
  $("body").addClass("chrome");
}

/*
    Modify jquery fileupload's onAdd method. This method recreates
    the file object pointer and changes the name. The name change allows
    users to drag and drop directories and those directories are
    recreated on swift.
*/
$.blueimp.fileupload.prototype._onAdd = function (e, data) {
  var that = this,
    result = true,
    options = $.extend({}, this.options, data),
    files = data.files,
    filesLength = files.length,
    limit = options.limitMultiFileUploads,
    limitSize = options.limitMultiFileUploadSize,
    overhead = options.limitMultiFileUploadSizeOverhead,
    batchSize = 0,
    paramName = this._getParamName(options),
    paramNameSet,
    paramNameSlice,
    fileSet,
    i,
    j = 0;
  if (limitSize && (!filesLength || files[0].size === undefined)) {
    limitSize = undefined;
  }
  if (!(options.singleFileUploads || limit || limitSize) ||
          !this._isXHRUpload(options)) {
    fileSet = [files];
    paramNameSet = [paramName];
  } else if (!(options.singleFileUploads || limitSize) && limit) {
    fileSet = [];
    paramNameSet = [];
    for (i = 0; i < filesLength; i += limit) {
      fileSet.push(files.slice(i, i + limit));
      paramNameSlice = paramName.slice(i, i + limit);
      if (!paramNameSlice.length) {
        paramNameSlice = paramName;
      }
      paramNameSet.push(paramNameSlice);
    }
  } else if (!options.singleFileUploads && limitSize) {
    fileSet = [];
    paramNameSet = [];
    for (i = 0; i < filesLength; i = i + 1) {
      batchSize += files[i].size + overhead;
      if (i + 1 === filesLength ||
            ((batchSize + files[i + 1].size + overhead) > limitSize) ||
            (limit && i + 1 - j >= limit)) {
        fileSet.push(files.slice(j, i + 1));
        paramNameSlice = paramName.slice(j, i + 1);
        if (!paramNameSlice.length) {
          paramNameSlice = paramName;
        }
        paramNameSet.push(paramNameSlice);
        j = i + 1;
        batchSize = 0;
      }
    }
  } else {
    paramNameSet = paramName;
  }
  data.originalFiles = files;
  $.each(fileSet || files, function (index, element) {

    /****************** Swift browser edits here ******************/
    /*
        A new File object is created using "element". This new file
        has a different ".name". This new name allows swift to
        create pseudo folders. The end result is the file structure
        that is dragged and dropped in swiftbrowser is preserved on
        swift.
    */

    if (element.relativePath) {
      element = new File([element], element.relativePath + element.name, {type: "text/plain"});

    } else if (element.webkitRelativePath) {
      element = new File([element], element.webkitRelativePath, {type: "text/plain"});

    }
    var newData = $.extend({}, data);
    newData.files = fileSet ? element : [element];
    newData.paramName = paramNameSet[index];
    that._initResponseObject(newData);
    that._initProgressObject(newData);
    that._addConvenienceMethods(e, newData);
    result = that._trigger(
      'add',
      $.Event('add', {delegatedEvent: e}),
      newData
    );
    return result;
  });
  return result;
};
