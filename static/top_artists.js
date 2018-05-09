$(document).ready(function(){
    $.get('/top_artists_source', function(data, status){
        console.log(data)
        $('.container').append('<div id="card_deck" class="card-deck"></div>');
        for (var i = 0; i < data.length; i++ ){
            if (data[i].images.length != 0){
                var recommended_artist_html = `
                <div class="card">
                    <img class="card-img-top img-fluid" src="${data[i].images[0].url}" />
                    <div class="card-body">
                        <h5 class="card-title">${data[i].name}</h5>
                        <p class="card-text">Genre: ${data[i].genres[0]}</p>
                        <a href="/artist/${data[i].id}" class="btn btn-primary">View Artist Page</a>
                    </div>
                </div>
                `;
                $('#card_deck').append(recommended_artist_html)
            }
        }
    });
});