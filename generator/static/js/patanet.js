$(function() {
    $(".script").toggle();

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

    var select_artist_songs = function(){
        $("input.artist ").change(function(){
            var checked = $(this).is(":checked");
            $(this).siblings("ul").children("li").each(function() {
                $(this).children("input").prop("checked", checked);
            })
        });

        $("input.artist").removeAttr("name");

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

    var add_songs = function(){
        $("#add_songs").click(function(){
            $("#add_songs_form").submit();
            return false;
        });
    }

    // Execute code
    ordering();
    select_artist_songs();
    add_songs();
});
