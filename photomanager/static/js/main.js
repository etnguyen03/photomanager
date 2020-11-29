$(document).ready(function() {
   $(".img-spinner").on("load", function() {
       $(this).parent().children(".spinner-wrapper").hide();
   })
});