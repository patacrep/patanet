
//function to prevent the user from accidentally leaving a page without saving its changes
var unsaved = false;
function unsaved_changes(){
    if(!unsaved){
        window.onbeforeunload = function (e) {
          var message = "Your have unsaved changes on the page.",
          e = e || window.event;
          // For IE and Firefox
          if (e) {
            e.returnValue = message;
          }

          // For Safari
          return message;
        };

    }
    unsaved = true;
}


$(function() {
    
    $("form").submit(function(e){
        window.onbeforeunload = null;
    });

    $(".script").toggle();

    var ordering = function(){
        // Make the ordering class sortable, with jquery-ui
        $( ".ordering" ).sortable({
            axis: "y",
            scrollSensitivity: 100,
            stop: function( event, ui ) {}
        });

        $(".ordering li .item-rank").hide();
        
        var btn = $('<a>', {class:"remove button-link"});

        // A click on remove add a 'X' in the input and hide it.
        btn.click(function(){
            var line = $(this).parent("li");
            var input = line.children('input.item-rank');
            var rank = input.attr('value').toUpperCase();
            if(rank == "X"){
                input.attr("value", "0");
                line.removeClass('removed');
            } else {
                input.attr("value", "X");
                line.addClass('removed');
            }
            unsaved_changes();
            $(".ordering").trigger("sortstop");
            })
        btn.appendTo(".ordering li");
        
        // Compute the rank for all the items
        $( ".ordering" ).on( "sortstop", function( event, ui ) {
              var i = 1;
              $('.ordering').children('li').each(function() {
                  var input = $(this).children('.item-rank');
                  if (input.attr("value") != "X") {
                    if(input.attr("value") != i){
                        unsaved_changes();
                        input.attr("value", i);
                    }
                    i+=1;
                  }
              });
        });
    }

    var select_artist_songs = function(){
        $("input.artist").change(function(){
            var checked = this.checked;
            var songs = $(this).siblings("ul").children("li").children("input.select_song:not(:disabled)");
            songs.each(function() {
                this.checked = checked;
            })
            songs.first().trigger('change');
        });

        $("input.select_song").change(function(){
            var artist = $(this).parents("ul").siblings("input.artist");
            var songs = artist.siblings("ul").children("li").children("input.select_song");
            var songs_checked = songs.filter(":checked");
            var nb_checked = songs_checked.length;
            var nb_songs = songs.length;

            artist = artist.get(0);

            artist.indeterminate = (nb_checked > 0 && nb_checked < nb_songs);
            artist.checked = (nb_checked == nb_songs);
        });
        $("ul > li:first-child > input.select_song").trigger('change');
    }

    var auto_template_name = function(){
        var selects = $('form.new_layout select');
        var input_name = $('form.new_layout #id_name');

        selects.change(function(){
            var name = 'A4';
            for (var i = selects.length - 1; i >= 0; i--) {
                name += '-' + selects[i].options[selects[i].selectedIndex].value;
            };
            input_name.attr('value', name);
        });
        input_name.change(function(){
            selects.off('change');
        });

        var current_name = input_name.attr('value');

        if(typeof current_name !== 'string' || current_name.length == 0){
            selects.trigger('change');
        }
    }

    // Execute code
    ordering();
    select_artist_songs();
    auto_template_name();
});


function songbook_details(elt, e){
    if(e.target.tagName !== 'A'){
        $(elt.parentNode).toggleClass('see_more');
    }
}
