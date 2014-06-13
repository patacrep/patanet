$(function() {
  $(".no-js").hide();

  var ordering = function(){
      // Make the ordering class sortable, with jquery-ui
      $( ".ordering" ).sortable({
          stop: function( event, ui ) {}
      });

      $(".ordering li .item-rank").hide();
      $('.remove').clone().css("display","inline").prependTo(".ordering li");
      // Compute the rank for all the items
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
      // A click on remove add a 'X' in the input and hide it.
      $(".remove").click(function(e){
          $(this).parent("li").children('input').attr("value", "X");
          $(this).parent("li").hide();
          $(".ordering").trigger("sortstop");
      });
  }

  ordering();
});
