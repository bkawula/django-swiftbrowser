$('#close-upload').on('click', function(){
    $('#fileForm').foundation('reveal', 'close');
});

var files_added = 0; /* Track files added to the upload. */
var files_processed = 0; /* Track files that are processed.*/
var files_uploaded = 0; /* Track successful uploads. */
$( function() {
    'use strict';

    /*
        Initialize the jQuery File Upload widget.

        Default options are defined by the package,
        however users may extend and define their
        own options.
    */

    var formData = $('#fileupload').serializeArray();
    formData.push(
        {name:"redirect",value:""}
    );

    $('#fileupload').fileupload({
        formData: formData,
        url: $(this).attr('action'),
        method:'POST',
        dataType:'text',
        sequentialUploads: true,
        recalculateProgress: false,
        previewMaxWidth:100,
        previewMaxHeight:100
    })

    // Keep a counter of files as they are added.
    .bind('fileuploadadd', function (e, data) {
        files_added += 1;
    })

    .bind('fileuploaddone', function (e, data) {
        files_uploaded += 1;
    })

    .bind('fileuploadprocessstart', function (e) {
        $('#preloadmsg').hide();
        
		$('.fileupload-progress').show();
        $('#start-upload').removeClass('disabled');
        $('#cancel-upload').removeClass('disabled');
        if (files_added > 1) {
            $('.file-progress').show();
        }
    })

    .bind('fileuploadsend', function (e, data) {
        Foundation.libs.reveal.settings.close_on_background_click = false;
        $('#close-upload').off().addClass('disabled');

        $.each(data.files, function (index, file) {

            $('#fileForm').foundation({reveal : {close_on_background_click: false,close_on_esc:false}});
        });
    })
	
	.bind('fileuploadfail', function (e, data) {
		
		
	})
	
	
    // Keep a counter of files as they are processed.
    .bind('fileuploadalways', function (e, data) {
        files_processed += 1;
        
        // If all fiels have been processed, close the form.
        if (files_processed == files_added) {
            closeForm();
            loadTable();
        }
    })
    .addClass('fileupload-processing');

});
$('#cancel-upload').click(function(){
	$('#fileForm').foundation({reveal : {close_on_background_click: true,close_on_esc:true}});
	$('#preloadmsg').show();
	$('.fileupload-progress').hide();
	files_uploaded = 0;
	files_added = 0;
	files_processed = 0;
    $('#start-upload').addClass('disabled');
    $('#cancel-upload').addClass('disabled');
    $('#close-upload').on('click', function(){
        $('#fileForm').foundation('reveal', 'close');
    }).removeClass('disabled');
});

function closeForm() {
    $('#fileForm').foundation({reveal : {close_on_background_click: true,close_on_esc:true}});

    setTimeout(function(){
        $('#fileForm').foundation('reveal', 'close');
        setTimeout(function(){
            $('#preloadmsg').show();
            $('.fileupload-progress').hide();
            $('#start-upload').addClass('disabled');
            $('#cancel-upload').addClass('disabled');
            $('#close-upload').on('click', function(){
                $('#fileForm').foundation('reveal', 'close');
            }).removeClass('disabled');
        }, 250);
    }, 250);

    if(files_uploaded > 0) {
        $('#messages').html(
            '<div data-alert class="alert-box success header-alert">' +
                '<div class="row" >' +
                    '<div class="small-12 columns">' +
                        '<strong>Success.</strong> ' + files_uploaded +
                        ' files were added. <a href="#" class="close">&times;</a>' +
                    '</div>' +
                '</div>' +
            '</div>'
        );
    }
	files_uploaded = 0;
	files_added = 0;
	files_processed = 0;
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
            var element = new File([element], element.relativePath + element.name, {type: "text/plain"});

        } else if (element.webkitRelativePath){
            console.log(typeof element.webkitRelativePath);
            var element = new File([element], element.webkitRelativePath + element.name, {type: "text/plain"});

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
}
