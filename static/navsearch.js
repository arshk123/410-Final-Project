$(document).ready(function(){
    $("#navsearch").autocomplete({
        source:function(request, response) {
            console.log(request.term)
            $.getJSON("/navsearch",{
                q: request.term, // in flask, "q" will be the argument to look for using request.args
            }, function(data) {
                response(data.matching_results); // matching_results from jsonify
            });
        },
        minLength: 3,
        select: function(event, ui) {
            window.location.replace("/artist/" + ui.item.value);
        }
    });
});