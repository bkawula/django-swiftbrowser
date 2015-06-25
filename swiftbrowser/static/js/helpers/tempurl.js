/* This is a helper file for tasks completed in tempurls. */

$(function () {
    //Close tempurl modal
    $('#close-tempurl').on('click', function (){
        $('#tempurl').foundation('reveal', 'close');
    });

    //Select the tempurl on modal open.
    $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {

        $("#generated-tempurl").select();

        //Select the tempurl on icon click.
        $("#highlight-icon").on("click", function () {
            $("#generated-tempurl").select();
        });

       /* Ajax for custom temp url form submission. */
       $("form#custom-temp-url").submit(function(event) {

            var formData = {
                'days'              : $('input[name=days]').val(),
                'hours'             : $('input[name=hours]').val(),
                'csrfmiddlewaretoken' : $('input[name=csrfmiddlewaretoken]').val()
            };

            $.ajax({
                type        : 'POST',
                url         : $("form#custom-temp-url").attr("action"),
                data        : formData,
                dataType    : 'html',
                encode          : true
            })
            // Populate the modal with the new tempurl html.
            .done(function(data) {

                $("#tempurl").html(data);

                // New html has been loaded with no js events.
                // Thus we manually trigger the events form this page.
                $('#tempurl').trigger('opened.fndtn.reveal');
            });

            // stop the form from submitting the normal way and refreshing the page
            event.preventDefault();

        });
    });
});