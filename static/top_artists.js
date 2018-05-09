$(document).ready(function(){
    $.get('/top_artists_source', function(data, status){
        console.log(data)
        $('.container').append('<div class="row"><div id="card-deck" class="card-deck"></div></div>');
        for (var i = 0; i < data.length; i++ ){
            if (data[i].images.length != 0){
                var recommended_artist_html = `
                <div class="col-4">
                    <div class="card" style="width: 20rem height:40rem;">
                        <img class="card-img-top img-fluid" src="${data[i].images[0].url}" />
                        <div class="card-body">
                            <h5 class="card-title">${data[i].name}</h5>
                            <p class="card-text">Genre: ${data[i].genres[0]}</p>
                            <a href="/artist/${data[i].id}" class="btn btn-primary">View Artist Page</a>
                        </div>
                    </div>
                </div>
                `;
                $('#card-deck').append(recommended_artist_html)
            }
            else{
                var recommended_artist_html = `
                <div class="col-4">
                    <div class="card" style="width: 20rem  height:40rem;">
                        <img class="card-img-top img-fluid" src="/static/album-art-empty.png" />
                        <div class="card-body">
                            <h5 class="card-title">${data[i].name}</h5>
                            <p class="card-text">Genre: ${data[i].genres[0]}</p>
                            <a href="/artist/${data[i].id}" class="btn btn-primary">View Artist Page</a>
                        </div>
                    </div>
                </div>
                `;
                $('#card-deck').append(recommended_artist_html)
                // $('#row' + i).append('<a href="#" class="list-group-item list-group-item-action flex-column align-items-start"><div class="d-felx w-100 justify-content-between"><h5 class="mb-1">'+data[i].name+'</h5></div></a>')
            }
        }
    });
});