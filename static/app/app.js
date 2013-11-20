if (!window.ziply){
    window.ziply = {};
}

ziply.deleteConfirm = function( url ){
    var r = confirm("Delete it?");
    if ( r == true ){
        window.location.href = url;
    }
}

$(document).ready(function() {
  $( "#loading" ).hide();
  $( "#simple-menu" ).sidr({
    speed:200,
    side:"left"
  });
});