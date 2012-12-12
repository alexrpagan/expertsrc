$(function() {
    var opts = {
        lines: 11, // The number of lines to draw
        length: 5, // The length of each line
        width: 4, // The line thickness
        radius: 10, // The radius of the inner circle
        rotate: 0, // The rotation offset
        color: '#000', // #rgb or #rrggbb
        speed: 1, // Rounds per second
        trail: 74, // Afterglow percentage
        shadow: false, // Whether to render a shadow
        hwaccel: false, // Whether to use hardware acceleration
        className: 'spinner', // The CSS class to assign to the spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        top: '0', // Top position relative to parent in px
        left: 'auto' // Left position relative to parent in px
    };

    var spinner = new Spinner(opts);
    var check = $('input[name=check]').val() == 'True';
    var poll_for_batches;
    var max_attempts = 5;
    var num_batches = $('input[name=num_batches]').val();

    if (check) {
        var uid = $('input[name=uid]').val();
        (poll_for_batches = function(num_attempts, max_attempts){
            if( num_attempts === 0 ){
                $('#status').show("slow").append('Checking for new batches...');
                $('#spinner').html(spinner.spin().el);
            }
            setTimeout( function () {
            var most_recent_ts = $('input[name=most_recent]').val();
                $.ajax({
                    url: url_check_for_new_batches,
                    success: function(data){
                        if(data == 'None'){
                            if(num_attempts < max_attempts){
                                poll_for_batches(num_attempts + 1, max_attempts);
                            } else if(num_attempts == max_attempts){
                                spinner.stop();
                                $('#status').hide();
                            }
                        } else {
                            $('#status').hide();
                            if( num_batches === 0 ){
                                $('.alert').hide();
                                $('#batches').show();
                            }
                            spinner.stop();
                            $('#batches > tbody:first').prepend(data).hide().show("slow");
                        }
                    },
                    type: "POST",
                    data: {
                        most_recent : most_recent_ts,
                        uid : uid
                    },
                    dataType: "html",
                    timeout: 50000,
                    cache: false
                });
            }, 1000);
        })( 0 , max_attempts - 1 );
    }
});
