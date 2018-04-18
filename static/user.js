$(document).ready(function(){
    $.get('/user/1/recommendations', function(data, status){
        console.log(data)
        var row_number = 0;
        for (var i = 0; i < data.length; i++ ){
            if (i % 3 == 0){
                row_number++;
                $('.container').append('<div id="row' + row_number + '" class="row"></div>');

            }
            if (data[i].images.length != 0){
                var recommended_artist_html = `
                <div class="col-4">
                    <div class="card" style="width: 18rem;">
                        <img class="card-img-top" src="${data[i].images[0].url}" />
                        <div class="card-body">
                            <h5 class="card-title">${data[i].name}</h5>
                            <p class="card-text">Genre: ${data[i].genres[0]}</p>
                            <a href="/artist/${data[i].id}" class="btn btn-primary">View Artist Page</a>
                        </div>
                    </div>
                </div>
                `;
                $('#row' + row_number).append(recommended_artist_html)
            }
            else{
                var recommended_artist_html = `
                <div class="col-4">
                    <div class="card" style="width: 18rem;">
                        <div class="card-body">
                            <h5 class="card-title">${data[i].name}</h5>
                            <p class="card-text">Genre: ${data[i].genres[0]}</p>
                            <a href="/artist/${data[i].id}" class="btn btn-primary">View Artist Page</a>
                        </div>
                    </div>
                </div>
                `;
                $('#row' + row_number).append(recommended_artist_html)
                // $('#row' + i).append('<a href="#" class="list-group-item list-group-item-action flex-column align-items-start"><div class="d-felx w-100 justify-content-between"><h5 class="mb-1">'+data[i].name+'</h5></div></a>')
            }
        }
    });
});