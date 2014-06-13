$(function() {
  $(".no-js").hide();

  $( ".ordering" ).sortable({
      stop: function( event, ui ) {}
  });

  $(".ordering li .item-rank").hide();
  $('.remove').clone().css("display","inline").prependTo(".ordering li");

  $( ".ordering" ).on( "sortstop", function( event, ui ) {
        var i = 1;
        $('.ordering').children('li').each(function() {
            var input = $(this).children('.item-rank');
            if (input.attr("value") != "X") {
              input.attr("value", i);
              i+=1;
            }
        });
  });

  $(".remove").click(function(e){
      $(this).parent("li").children('input').attr("value", "X");
      $(this).parent("li").hide();
      $(".ordering").trigger("sortstop");
  });

});
