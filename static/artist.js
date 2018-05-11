$(document).ready(function(){
    $('.rate').click(function(){
        $('.disabled').attr('class', 'btn btn-lg btn-dark rate');
        $(this).attr('class', 'btn btn-lg btn-dark disabled rate');

        var spotify_id = $(this).attr('id').split(' ')[0]
        var rating = $(this).attr('id').split(' ')[1]

        console.log($(this).attr('id'))
        $.post('/artist/rate/'+spotify_id, {rating: parseInt(rating)}, function(result){
            location.reload();
        });
    });
});