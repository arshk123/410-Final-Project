$(document).ready(function(){
    $('#signupForm').submit(function(event){
        event.preventDefault();
        var password = $('#passwordSignup').val();
        var confirmed_password = $('#passwordConfirm').val();


        if (password != confirmed_password){
            var mismatched_password_html = `<div class="col offset-md-1">
                                                <div class="col-sm-10">
                                                    <span class="text-danger">Passwords do not match.</span>
                                                </div>
                                            </div>`
            $('#signupForm').append(mismatched_password_html)
        }
        else {
            $.ajax({
                type: 'POST',
                method: 'POST',
                dataType: 'json',
                data: $(this).serialize(),
                url: '/signup',
                success: function(response){
                    console.log(response)
                    window.location.replace(response.redirect_url);
                }
            }
            );
        }
    });
})