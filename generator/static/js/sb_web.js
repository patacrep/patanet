$(function() {
  $( ".ordering" ).sortable({
      stop: function( event, ui ) {}
  });

  //$(".ordering li input").css("display", "none");

  $( ".ordering" ).on( "sortstop", function( event, ui ) {
        $('.ordering').children('li').each(function(i) {
            $(this).children('input').attr("value", i+1);
        });
  });
});
