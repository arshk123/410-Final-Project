$(document).ready(function(){
    $('.rate').click(function(){
        $('.disabled').attr('class', 'btn btn-lg btn-dark rate')
        $(this).attr('class', 'btn btn-lg btn-dark disabled rate')
    })
});