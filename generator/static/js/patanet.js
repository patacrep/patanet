
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

    //CSRF management for JQuery
    $.ajaxSetup({ 
         beforeSend: function(xhr, settings) {
             function getCookie(name) {
                 var cookieValue = null;
                 if (document.cookie && document.cookie != '') {
                     var cookies = document.cookie.split(';');
                     for (var i = 0; i < cookies.length; i++) {
                         var cookie = jQuery.trim(cookies[i]);
                         // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
             }
             if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                 // Only send the token to relative URLs i.e. locally.
                 xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
             }
         } 
    });

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
    
    var increase_dataset_value = function(elt, incr){
        var value = parseInt(elt.dataset.value);
        value += incr;
        elt.dataset.value = value;
    }

    var toggle_add_remove_all_button = function(elt){
        var max = parseInt(elt.dataset.max);
        var value = parseInt(elt.dataset.value);
        var btn = $(elt).siblings('button').first();
        if(value < max){
            btn.addClass('clickable');
        } else {
            btn.removeClass('clickable');
        }
    }

    var ajax_change_artist_songs = function(elt, add_song){
        // disable to prevent the user from clicking it again
        // before the whole processing is done
        elt.disabled = true;
        var container = $(elt).closest(".item-container");
        if(add_song){
            container.addClass('adding');
        } else {
            container.addClass('deleting');
        }

        var ids = [];
        var inputs = container.find('.songs li input');
        inputs.each(function(){
            ids.push(this.value);
        });

        var data = { 
            'songs[]' : ids,
            'current_songbook' : $('#current_songbook_id').get(0).value
        };

        var url = baseurl+'songbooks/';
        url += (add_song) ? 'add' : 'remove';
        url += '-song';

        $.post(url, data)

            // successfully treated
            .done(function(data) {

                // but something wrong on server side
                if(!data.success){
                    // we have messages to display
                    if(data.success === false && data.messages){
                        var messages_container = $('ul.messages');
                        $.each(data.messages, function(i, value){
                            var new_message = document.createElement('li');
                            new_message.className = value.tags;
                            new_message.innerHTML = value.msg;
                            messages_container.append(new_message);
                        })
                        window.scrollTo(0, 0);
                        return;
                    }
                    console.log('Something wrong on the server side :');
                    console.log(data);
                    if(confirm('Unexpected server response, you should try to reload the page')){
                        document.location.reload();
                    }
                    return;
                }

                var song_added = 0;
                inputs.each(function(){
                    if(this.checked != add_song){
                        this.checked = add_song;
                        song_added += 1;
                        if(add_song){
                            $(this.parentNode).addClass('added');
                        } else {
                            $(this.parentNode).removeClass('added');
                        }
                    }
                });

                song_added = (add_song) ? song_added : -song_added;

                // update the global counter
                var global_counter = $('#current_songbook_count').get(0);
                increase_dataset_value(global_counter, song_added);

                // update the artist counter
                var artist_counter = $(elt).closest(".item-container").find(".intersection").get(0);
                if(artist_counter){
                    increase_dataset_value(artist_counter, song_added);
                    toggle_add_remove_all_button(artist_counter);
                }

            })
            // failure
            .fail(function(data) {
                console.log('Something wrong on the server side :');
                console.log(data.responseText);
                if(confirm('Unexpected server response, you should try to reload the page')){
                    document.location.reload();
                }
            })
            // anyway
            .always(function() {
                if(add_song){
                    container.removeClass('adding');
                } else {
                    container.removeClass('deleting');
                }
                elt.disabled = false;
            });
    }

    var ajax_change_song = function(elt, add_song){
        // disable to prevent the user from clicking it again
        // before the whole processing is done
        elt.disabled = true;
        $(elt.parentNode).addClass('updating');

        var id = elt.value;
        var data = { 
            'songs[]' : id,
            'current_songbook' : $('#current_songbook_id').get(0).value
        };

        var url = baseurl+'songbooks/';
        url += (add_song) ? 'add' : 'remove';
        url += '-song';

        $.post(url, data)

            // successfully treated
            .done(function(data) {

                // but something wrong on server side
                if(!data.success){
                    elt.checked = !add_song;

                    // we have messages to display
                    if(data.success === false && data.messages){
                        var messages_container = $('ul.messages');
                        $.each(data.messages, function(i, value){
                            var new_message = document.createElement('li');
                            new_message.className = value.tags;
                            new_message.innerHTML = value.msg;
                            messages_container.append(new_message);
                        })
                        window.scrollTo(0, 0);
                        return;
                    }
                    console.log('Something wrong on the server side :');
                    console.log(data);
                    if(confirm('Unexpected server response, you should try to reload the page')){
                        document.location.reload();
                    }
                    return;
                }
                if(elt.checked){
                    $(elt.parentNode).addClass('added');
                } else {
                    $(elt.parentNode).removeClass('added');
                }

                song_added = (elt.checked) ? 1 : -1;

                // update the global counter
                var global_counter = $('#current_songbook_count').get(0);
                increase_dataset_value(global_counter, song_added);

                // update the artist counter
                var artist_counter = $(elt).closest(".item-container").find(".intersection").get(0);
                if(artist_counter){
                    increase_dataset_value(artist_counter, song_added);
                    toggle_add_remove_all_button(artist_counter);
                }

            })
            // failure
            .fail(function(data) {
                console.log('Something wrong on the server side :');
                console.log(data.responseText);
                if(confirm('Unexpected server response, you should try to reload the page')){
                    document.location.reload();
                }
                elt.checked = !add_song;
            })
            // anyway
            .always(function() {
                var parent = $(elt.parentNode);
                parent.removeClass('updating');
                elt.disabled = false;
            });
    }

    var song_selection_with_ajax = function(){
        var checkboxes = $('form#add_songs_form input.song_selection');

        // add callbacks onClick
        checkboxes.each(function(){
            label = $(this.parentNode);
            if(this.checked){
                this.disabled = false;
                label.addClass('added');
            }
            label.addClass('ajax');
            $this = $(this);
            $this.change(function(){
                ajax_change_song(this, this.checked);
            });

        })

        // hide "add selection" buttons
        $('form#add_songs_form > button.selection').hide();


        // attach callbacks to "add/remove all" buttons
        $('form#add_songs_form .item-container h2 button').each(function(){
            $(this).click(function(){
                var add = (this.dataset.icon == 'add-multiple');
                ajax_change_artist_songs(this, add);
            });
        });

        // show "add/remove all" 
        $('form#add_songs_form .item-container h2 .intersection').each(function(){
            toggle_add_remove_all_button(this);
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
    auto_template_name();
    song_selection_with_ajax();
});


function toggle_see_more(elt, e){
    switch(e.target.tagName){
        case 'A':
        case 'INPUT':
        case 'LABEL':
        break;

        default:
        $(elt).toggleClass('see_more');
    }
}
