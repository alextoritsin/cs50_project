// Create an array of companies
var companies  = [];

function loadComp(){
    $.getJSON('/companies', function(data, status, xhr){
        for (var i = 0; i < data.length; i++) {
            companies.push(data[i]);
        }
    });
};
loadComp();

$(document).ready(function() {

    // Overrides the default autocomplete filter function
    // to search only from the beginning of the string
    $.ui.autocomplete.filter = function (array, term) {
        var matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex(term), "i");
        return $.grep(array, function (value) {
            return matcher.test(value.label || value.value || value);
        });
    };
    // split and extract functions
    function split( val ) {
        return val.split( /,\s*/ );
    }
    function extractLast( term ) {
    return split( term ).pop();
    }

    // Initialize jquery autocomplete
    $("#name")
    // don't navigate away from the field on tab when selecting an item
    .on( "keydown", function( event ) {
        if ( event.keyCode === $.ui.keyCode.TAB &&
            $( this ).autocomplete( "instance" ).menu.active ) {
          event.preventDefault();
        }
    })
    .autocomplete( {
        minLength: 3,
        autoFocus: true,
        source: function (request, response) {
            var results = $.ui.autocomplete.filter(companies, extractLast(request.term));
            response(results.slice(0, 10));
        },
        focus: function() {return false;},
        select: function( event, ui ) {
            var terms = split( this.value );
            // remove the current input
            terms.pop();
            // add the selected item
            terms.push( ui.item.value );
            // add placeholder to get the comma-and-space at the end
            terms.push( "" );
            this.value = terms.join( ", " );
            return false;
        }
    });
});
