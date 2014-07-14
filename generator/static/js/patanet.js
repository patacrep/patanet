
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
        $("input.artist ").change(function(){
            var checked = this.checked;
            $(this).siblings("ul").children("li").children("input").each(function() {
                this.checked = checked;
            })
        });

        var all_checked = function(artist, songs){
            // This function is a workaround a bug: with only the second condition
            // (art_checked == false), two checkbox had to be unchecked before
            // the artist checkbox was unchecked.
            var art_checked = artist.is(":checked");
            if (art_checked) {
                if (songs.length == songs.filter(":checked").length + 1) {
                    return true
                }
                else {
                    return false
                }
            }
            else {
                if (songs.length == songs.filter(":checked").length) {
                    return true
                }
                else {
                    return false
                }
            }
        }

        $("input.select_song ").change(function(){
            var songs = $(this).parent("li").siblings("li").children("input.select_song");
            var artist = $(this).parents("ul").siblings(".artist");
            artist.prop("checked", all_checked(artist, songs));
        });
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
