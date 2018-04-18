$(document).ready(function(){
    $('#signOut').click(function(){
        $.post('/logout', function(data){
            window.location = data;
        });
    });
});
