$(document).ready(function() {
    $(".img-spinner").on("load", function() {
        $(this).parent().children(".spinner-wrapper").hide();
    });

    $('.img-spinner-lazy').lazy({
        afterLoad: function(element) {
            element.parent().children(".spinner-wrapper").hide();
        }
    });
});