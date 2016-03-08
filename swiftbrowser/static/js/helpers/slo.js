/*
    Disable form in favour of using Javascript to handle it.
*/
$('#slo-upload form').submit(function (e) {
    e.preventDefault();
});

/*
    Set event for initializing a SLO upload.
*/
$('#slo-upload button.upload').click(slo_upload);


var xhrs = [];

/*
  Create a SLO from the selected file.
*/
function slo_upload() {

    //Display progress bar
    $(".css-progress-wrap").toggle(true);

    //Display and bind the cancel button.
    $("#slo-upload button.cancel-slo-button").toggle(true)
    .click(function () {

        //Hide cancel button
        $(this).toggle(false);

        //Hide progress bar.
        $(".css-progress-wrap").toggle(false);

        //Abort the latest xhr request to the first so we don't end up
        //uploading i + c but not i.
        for (var i = xhrs.length - 1; i >= 0; i--) {
            xhrs[i].abort();
        }
    });

    var file = $("#slo-upload input")[0].files[0];
    if (!file) {
        return;
    }

    var file_name = file.name;
    var formData = {
        file_name            : file_name,
        csrfmiddlewaretoken  : $('input[name=csrfmiddlewaretoken]').val(),
        file_size            : file.size
    };

    /*
        The following call interacts with the swiftbrowser backend to determine
        what size each segment of this file should be. We will receive a
        segment number which tells us where to start uploading. Uploading not
        starting at number 1 implies this upload is a continuation of a
        previous upload.
    */
    $.ajax({
        type        : 'POST',
        url         : $("#slo-upload form").attr("data-initial-action"),
        data        : formData,
        dataType    : 'html',
        encode      : true,
        asych       : false
    })

    .success(upload_segments)

    .error(function(error) {
        console.log(error.responseText);
    });
}

/*
    Given the data object from the "initialize slo" request, upload segments
    of the file.
*/
function upload_segments(data) {

    var file = $("#slo-upload input")[0].files[0];

    data = $.parseJSON(data); /* Tell us what segment to start at and the size of the file. */
    var segment_number = data.next_segment; /* The first segment to create. */
    var segment_size = data.segment_size; /* The server tells us what size the segments should be based ont the size of the file and segment number limits.*/

    var url = $("#slo-upload form .swift_url").val(); /* The url to POST to. Includes container and prefix (if there is one). */

    /*
        The segment will start at the product of the segment number minus one and the segment size.
        For example:
        - the 1st segment with segment size 200 will start at 0 (1 - 1 * 200).
        - the 4th segment with segment size 200 will start at 600 (4-1 * 100).
    */
    var segment_start = (segment_number - 1) * segment_size;

    /* The endpoint of the segment is the product of the segment number and segment size.
        For example the 3rd segment where segments are 200bytes will end at 600.
    */
    var segment_end = segment_number * segment_size;

    var segment; /* Holder for segments. */

    var done = segment_number - 1; /* Number of segments finished. */

    var total_segments = Math.ceil(file.size / segment_size);

    if (total_segments < segment_number) {
        create_manifest();
    }

    //While the entire file has not been uploaded, upload segments.
    while (segment_start < file.size) {

        /* Create a blob of the file based on the segment number. */
        segment = file.slice(segment_start, segment_end);

        var fd = new FormData($("#slo-form"));
        fd.append('max_file_size', $("#slo-upload form input[name='max_file_size']").val());
        fd.append('max_file_count', $("#slo-upload form input[name='max_file_count']").val());
        fd.append('expires', $("#slo-upload form input[name='expires']").val());
        fd.append('signature', $("#slo-upload form input[name='signature']").val());
        fd.append('redirect', "");
        var padded = pad(segment_number, 4);
        fd.append("FILE_NAME", segment, file.name + "_segments/" + padded);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', url, true);
        xhr.setRequestHeader("Accept", "text/plain, */*; q=0.01");
        xhr.onreadystatechange = function () {
            //On success, update the count.
            if (this.readyState == 4 && this.status == 201) {
                done++;

                //Update the progress bar.            done++;
                var getPercent = (done/total_segments);
                var getProgressWrapWidth = $('#slo-upload .css-progress-wrap').width();
                var progressTotal = getPercent * getProgressWrapWidth;
                var animationLength = 500;

                // on page load, animate percentage bar to data percentage length
                // .stop() used to prevent animation queueing
                $('#slo-upload .css-progress-bar').stop().animate({
                    left: progressTotal
                }, animationLength);

                if (done === total_segments) {

                    $("#slo-message").html("Segments uploaded. Creating manifest ...");

                    //Create manifest
                    create_manifest();
                }
            }
        };
        xhr.send(fd);
        xhrs.push(xhr);

        // Update the segment number, start and end position.
        segment_number++;
        segment_start = (segment_number - 1) * segment_size;
        segment_end = segment_number * segment_size;
    }
}

/*
    Submit query to Swiftbrowser to create the manifest for the SLO.
*/
function create_manifest() {

    var file = $("#slo-upload input")[0].files[0];
    var formData = {
        file_name            : file.name,
        csrfmiddlewaretoken  : $('input[name=csrfmiddlewaretoken]').val(),
        file_size            : file.size
    };

    /*
        The following call interacts with the swiftbrowser backend to determine
        what size each segment of this file should be. We will receive a
        segment number which tells us where to start uploading. Uploading not
        starting at number 1 implies this upload is a continuation of a
        previous upload.
    */
    $.ajax({
        type        : 'POST',
        url         : $("#slo-upload form").attr("data-create-manifest"),
        data        : formData,
        dataType    : 'html',
        encode      : true,
        asych       : false
    })

    .success(function (message)  {
        $('#fileForm').foundation('reveal', 'close');
        angular.element("#objecttable").scope().MessagesHandler.newSuccessMessage(message);
        angular.element("#objecttable").scope().refreshObjectTable();
    })

    .error(function(error) {
        $('#fileForm').foundation('reveal', 'close');
        angular.element("#objecttable").scope().MessagesHandler.newErrorMessage(error.responseText);
    });
}

/*
    Return a string with leading zeroes for the given int such that the
    resulting string has size number of digits.
*/
function pad(num, size) {
    var s = "000000000" + num;
    return s.substr(s.length-size);
}
