
// Create a namespace to store all patanet related functions
// (ideally, all functions must be registred there)
var patanet = {
    display_messages: function(messages){
        var messages_container = $('ul.messages');
        $.each(messages, function(i, value){
            var new_message = document.createElement('li');
            new_message.className = value.tags;
            new_message.innerHTML = value.msg;
            messages_container.append(new_message);
        })
        window.scrollTo(0, 0);
    },


    //function to prevent the user from accidentally leaving a page without saving its changes
    unsaved: false,
    unsaved_changes: function(){
        if(!patanet.unsaved){
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
        patanet.unsaved = true;
    }
};


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
         },
         error: function(data){
             ajax_failure(data);
         }
    });

    var ajax_failure = function(data){
        console.log('Something wrong on the server side :');
        console.log(data);
        if(confirm('Unexpected server response, you should try to reload the page')){
            document.location.reload();
        }
    }

    var set_rank_according_to_dom = function() {
        var i = 1;
        $('.ordering').children('li.orderable').each(function() {
          var input = $(this).children('.item-rank');
          if (input.attr("value") != "X") {
            if(input.attr("value") != i){
                patanet.unsaved_changes();
                input.attr("value", i);
            }
            i+=1;
          }
        });
    };

    var ordering = function(){

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
            patanet.unsaved_changes();
            set_rank_according_to_dom();
            })
        btn.appendTo(".ordering li.orderable");
        
        // Make the ordering class sortable, with jquery-ui
        $( ".ordering" ).sortable({
            axis: "y",
            scrollSensitivity: 100,
            items: '.orderable',
            // Compute the rank for all the items
            stop: set_rank_according_to_dom       
        });
    }

    var insert_new_section_via_js = function(){
        // show / hide the new_section containers
        $('form p.new_section').toggleClass('script');

        new_section_id = 0;
        new_section_dom = $('#new_section_dom').detach();
        new_section_dom.addClass('section');
        new_section_dom.removeAttr('id');

        var button = $('form p.new_section button');
        button.click(insert_new_section);
    }

    var append_to_id = function(elt, suffix){
        var new_id = elt.attr('id') + suffix;
        elt.attr('id', new_id);
    }

    var insert_new_section = function(){
        var new_section = new_section_dom.clone(true);
        new_section_id += 1;

        var name_input = new_section.find('input#new_section_');
        append_to_id(name_input, new_section_id);

        var rank_input = new_section.find('input#new_item_');
        append_to_id(rank_input, new_section_id);

        $('ol.item_list').append(new_section);
        set_rank_according_to_dom();
        patanet.unsaved_changes();
        name_input.focus();
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
                        patanet.display_messages(data.messages);
                        return;
                    }
                    ajax_failure(data);
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
                    ajax_failure(data);
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

    var letters_overview_background = function(){
        var letters = $('.letter_overview a');
        if(!letters.length){
            return;
        }
        var prefix_bg = letters.first().css('background-color');
        prefix_bg = prefix_bg.substr(0, prefix_bg.length - 4);
        $('.letter_overview a').each(function(){
            $this = $(this);
            var opa = $this.attr('data-weight');
            var new_bg = prefix_bg + opa + ')';
            $(this).css('background-color', new_bg);
        });
    }

    var toggle_see_more = function(elements){
        elements.click(function(e){
            switch(e.target.tagName){
                case 'A':
                case 'INPUT':
                case 'LABEL':
                break;

                default:
                    $(this).toggleClass('see_more');
            }
        })
    }

    var add_sorting_callback = function(elements){
        elements.click(function(e){
            var $this = $(this);
            var artist_first = $this.hasClass('by_artist');
            var line = $this.parents("li").first();
            var section_only = line.hasClass('section');
            var ask_confirmation = true;

            var $next = line.next();
            var to_sort = [];
            var links, artist, title;
            while($next.length > 0){
                // simply ignore the sections
                if($next.hasClass('section')){
                    if(section_only){
                        break
                    }
                    if(ask_confirmation && !confirm(line.attr("data-confirmation"))){
                        return;
                    }
                    ask_confirmation = false;
                    $next = $next.next();
                    continue;
                }
                links = $next.children('a')
                title = links[0].innerHTML.trim();
                artist = links[1].innerHTML.trim();
                if(artist_first){
                    to_sort.push([artist, title, $next]);
                } else {
                    to_sort.push([title, artist, $next]);
                }
                $next = $next.next();
            }

            to_sort.sort(function(a, b){
                    // if a should come after b, return 1
                    if (a[0] == b[0]) {
                        return a[1].localeCompare(b[1]);
                    } else {
                        return a[0].localeCompare(b[0]);
                    }
                }
            );

            for (var i = to_sort.length - 1; i >= 0; i--) {
                to_sort[i][2].insertAfter(line);
            };
            set_rank_according_to_dom();
        })

    }

    var check_all_downloads = function(){
        $('.update-me.task').each(function(index, elt){
            var task_id = elt.dataset.task;
            check_downloads(elt.parentNode, task_id);
        })
    }

    var check_downloads = function(element, task_id){

        function get_status(){


            var data = {};

            var url = baseurl+'songbooks/task/';
            url += task_id;
            url += '/link';

            $.post(url, data)

                // successfully treated
                .done(function(data) {
                    element.innerHTML = data.trim();
                    if($(element.firstChild).hasClass('update-me')){
                        // not rendered yet: need to check again
                        setTimeout(get_status, 4000);
                    }
                });
        }
        setTimeout(get_status, 5000);
    }

    // Execute code
    ordering();
    auto_template_name();
    song_selection_with_ajax();
    letters_overview_background();
    insert_new_section_via_js();
    toggle_see_more($('.item-container.songbook'));
    add_sorting_callback($('button.sort'));
    check_all_downloads();
});
