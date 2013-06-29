function nocuttingvalue() {
	var cuttingValues = $(".cuttingValue")
	var numTotalCutValues = cuttingValues.length;
	var numEmptyCutValues = cuttingValues.filter(function(){
		return this.value == '';
	}).length;
	var numZeroCutValues = cuttingValues.filter(function() {
		return this.value == '0'
	}).length;
	var numOneCutValues = cuttingValues.filter(function() {
		return this.value == '1'
	}).length;

	if ($("#overallcutvalue").val() == '' && numEmptyCutValues > 1) {
		alert('You haven\'t filled out a sufficient number of segment fields');
	}
	else if ( numZeroCutValues > 0 ) {
		alert('You cannot enter a value of 0 for a segment field');
	}
	
	else {
		return true;
	}
	return false;
}

$(function() {

	$("#cutaction").click( function() {
		return nocuttingvalue();
	});

	$("#cutapply").click( function() {
		return nocuttingvalue();
	});
});

$(function () {
    var timeToToggle = 150;
    $(".sizeradio").click( function() {
        var cuttingValueLabel = $(this).parents('.cuttingoptionswrapper').find('.cuttingoptionslabel');
        cuttingValueLabel.text("Segment Size:");

        var lastproportiondiv = $(this).parents('.cuttingoptionswrapper').find('.lastpropdiv');
        lastproportiondiv.animate({ opacity: 1 }, timeToToggle);
        lastproportiondiv.find('.lastpropinput').prop('disabled', false);
    });


    $(".numberradio").click( function() {
        var cuttingValueLabel = $(this).parents('.cuttingoptionswrapper').find('.cuttingoptionslabel');
        cuttingValueLabel.text("Number of Segments:");

        var lastproportiondiv = $(this).parents('.cuttingoptionswrapper').find('.lastpropdiv');
        lastproportiondiv.animate({ opacity: 0 }, timeToToggle);
        lastproportiondiv.find('.lastpropinput').prop('disabled', true);
    });

});

$(function () {
	var timeToToggle = 300;
    $(".indivcutbuttons").click( function() {
        var toggleDiv = $(this).parents('.individualpreviewwrapper').find('.cuttingoptionswrapper');
        toggleDiv.slideToggle(timeToToggle);
    });

});