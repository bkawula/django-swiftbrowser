$("#slo-upload a.close-reveal-modal").click(function () {
  location.reload();
});

update_progress_bar($("#folder-total").attr("data-total-objects"));


/*
    Make a post to the server to get the remaining number of objects in the
    folder.
*/
function update_progress_bar(total) {

    var formData = {
        csrfmiddlewaretoken  : $('input[name=csrfmiddlewaretoken]').val(),
        file_name            : "file_name",
    };

    $.ajax({
        type        : 'POST',
        url         : $("#delete-folder-form").attr("data-count-url"),
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

        $('.delete-slo-wrapper .css-progress-bar').stop().animate({
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
