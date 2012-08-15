format_values = function(values){
    $("#amount-min").val(values[0]);
    $("#amount-max").val(values[1]);
};

$(function() {
    $("#alloc-size-slider").slider({
	range: true,
	min: 1,
	max: 11,
	values: [1, 5],
	step: 2,
	slide: function( event, ui ) {
	    format_values(ui.values);
	}
    });
    format_values($("#alloc-size-slider").slider("values"));
});

$(function() {
    $("#price-slider").slider({
	range: "min",
	value: 20,
	min: 0,
	max: 100,
	slide: function( event, ui ) {
	    $("#price").val(ui.value)
	}
    });
    $("#price").val($("#price-slider").slider("value"))
});

$(function() {
    $("#confidence-slider").slider({
	range: "min",
	value: 80,
	min: 50,
	max: 100,
	slide: function( event, ui ) {
	    $("#confidence").val(ui.value)
	}
    });
    $("#confidence").val($("#confidence-slider").slider("value"))
});

get_modal_html = function (data) {
    id = data.id;
    html = '<div class="modal hide" id="view-' + id + '">' +
	'<div class="modal-header">' +
	'<button type="button" class="close" data-dismiss="modal">x</button><h3>Allocation Details</h3>' +
	'</div>' +
	'<div id="modal-'+id+'-content" class="modal-body"></div>' +
	'</div>';
    return html
};

fill_content = function (id, data) {
    test_content = "to go here:<br/> a level histogram <br/> a form for choosing another alloc";
    $("#modal-"+id+"-content").html(test_content);
}

// spinner options
var opts = {
    lines: 11, // The number of lines to draw
    length: 14, // The length of each line
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
    top: 'auto', // Top position relative to parent in px
    left: 'auto' // Left position relative to parent in px
};

truncate_float = function(num, places){
    return num.toString().substring(0, places + 2);
}

$(function() {
    $("#get-allocs").click(function(){
	// get the stuff that we need for the ajax call
	var batch_id = $('#batch_id').val();
	var question_ids = $('input[name=question_id]').map(function(){return $(this).val();}).get();
	var domain_id = $('input[name=domain_id]').val();
	var confidence = $('#confidence').val();
	var price = $('#price').val();
	var min_size = $('#amount-min').val();
	var max_size = $('#amount-max').val();
	var spinner = new Spinner(opts).spin();
	$("#get-allocs").text("Loading suggestions...");
	$('#spinner').html(spinner.el);
	$.post(
	    '/batch/get_allocation_suggestions/',
	    {
		batch_id : batch_id,
		question_ids : question_ids,
		domain_id : domain_id,
		min_size : min_size,
		max_size : max_size,
		price : price,
		confidence : confidence
	    },
	    function(data) {
		spinner.stop();
		$("#get-allocs").text("Get New Suggestions");
		if (data.status == 'OK'){
		    var cum_price = 0;
		    var cum_conf = 0;
		    var cum_workers = 0;

		    $("#error").hide();
		    $("#questions").show("slow");
		    for(var i=0 ; i < question_ids.length ; i++) {
			id = question_ids[i];
			alloc = data[id];
			if(alloc){
			    $('#num-workers-' + id).html(alloc.members.length);
			    cum_workers += alloc.members.length;
			    $('#confidence-' + id).html(truncate_float(alloc.confidence, 4));
			    cum_conf += alloc.confidence; 
			    $('#price-' + id).html(alloc.price);
			    cum_price += alloc.price;
			    $('#alloc-' + id).val(alloc.members.join());
			    if(!$('#view-'+id).length){
				$("body").append(get_modal_html({id:id}));
				$("#view-" + id).modal({show:false, keyboard:true});
			    }
			    fill_content(id, data);
			}
			$("#average-confidence").html(truncate_float(cum_conf/question_ids.length, 4));
			$("#average-alloc-size").html(truncate_float(cum_workers/question_ids.length, 4));
			$("#cumulative-price").html(truncate_float(cum_price, 6));
			$("#alloc-stats").show();
			
		    }
		} else {
		    $("#alloc-stats").hide();
		    $("#questions").hide();
		    $("#error").show('slow').html(data.msg);
		    setTimeout(function(){
			$("#error").fadeOut('slow');
		    }, 3000);
		}
	    },
	    "json"
	);
    });
});

$(function() {
    $("#commit-allocs").click(function(){
	var question_ids = $('input[name=question_id]').map(function(){return $(this).val();}).get();
	var allocs = $('input[name=allocation_selection]').map(function(){return $(this).val();}).get();
	var batch_id = $('#batch_id').val();
	var price = $('#cumulative-price').html();
	$('#status').attr('class', 'alert alert-info');
	$('#status').show('slow').html('Committing allocations...');
	$.post(
	    '/batch/commit_allocations/',
	    {
		batch_id : batch_id,
		question_ids : question_ids,
		allocs : allocs,
		price : price
	    },
	    function(data) {
		var msgTimeoutLength = 2000;
		$('#alloc-stats').hide();
		$('#questions').hide();
		if (data.status == 'success'){
		    $('#status').attr('class', 'alert alert-success');
		    $('#commit-allocs').attr('disabled', 'disabled');
		    setTimeout(function() {
			window.location = '/batches';
		    }, 2000);
		} else {
		    $('#status').attr('class', 'alert alert-error');
		    msgTimeoutLength = 5000;
		}
		$('#status').html(data.msg);
		setTimeout(function() {
		    $('#status').fadeOut('slow');
		}, msgTimeoutLength);
	    },
	    "json"
	);
    });
});

