/*jslint browser: true */
var chordDiagram = (function () {
    'use strict';

    var module = {},
        i,
        // 3 Header cell possibilities : empty, 'x', 'o'
        header_cell_empty = document.createElement('div'),
        header_cell_o = document.createElement('div'),
        header_cell_x = document.createElement('div');

    header_cell_o.appendChild(document.createElement('div'));
    header_cell_x.innerHTML = '&times;';

    function validateArray(array, size, max_value) {
        if ('object' !== typeof array) {
            return false;
        }

        for (i = 0; i < size; i += 1) {
            if ('number' !== typeof array[i] || array[i] % 1 !== 0 || array[i] < -1 || array[i] > max_value) {
                return false;
            }
        }
        return true;
    }



    function build_header(frets) {
        var header_row = document.createElement('div'),
            header_cell,
            num_strings = frets.length;
        header_row.className = 'header';

        for (i = 0; i < num_strings; i += 1) {

            if (frets[i] === 0) {
                header_cell = header_cell_o;
            } else if (frets[i] === -1) {
                header_cell = header_cell_x;
            } else {
                header_cell = header_cell_empty;
            }

            header_row.appendChild(header_cell.cloneNode(true));
        }
        return header_row;
    }

    function build_footer(frets, fingers) {
        var footer_row = document.createElement('div'),
            finger_cell,
            num_strings = fingers.length;
        footer_row.className = 'footer';

        for (i = 0; i < num_strings; i += 1) {
            finger_cell = document.createElement('div');

            if (frets[i] > 0) {
                if (fingers[i] === 0) {
                    finger_cell.innerHTML = 'T';
                } else if (fingers[i] > 0) {
                    finger_cell.innerHTML = fingers[i];
                }
            }

            footer_row.appendChild(finger_cell);
        }
        return footer_row;
    }


    module.build_diagram = function (frets, fingers) {

        var num_strings = frets.length,
            footer_row_needed = false,
            fret_min = 100,
            fret_max = 0,
            container,
            first_fret,
            fret,
            frets_row,
            fret_cell,
            fretno_cell,
            barre_start,
            barre_finish,
            barre_finger,
            barre_cell,
            knob_cell;

        if (!validateArray(frets, num_strings, 32)) {
            throw "Frets parameter format is invalid";
        }
        if (undefined !== fingers && !validateArray(fingers, num_strings, 4)) {
            throw "Fingers parameter format is invalid";
        }


        for (i = 0; i < num_strings; i += 1) {
            if (frets[i] > -1 && frets[i] > fret_max) {
                fret_max = frets[i];
            }
            if (frets[i] > 0 && frets[i] < fret_min) {
                fret_min = frets[i];
            }
            if ('object' === typeof fingers && fingers[i] !== -1) {
                footer_row_needed = true;
            }
        }

        container = document.createElement('div');
        container.className = 'chord-diagram';

        container.appendChild(build_header(frets));


        first_fret = fret_max > 5 ? fret_min : 1;

        for (fret = first_fret; fret < first_fret + 5; fret += 1) {
            frets_row = document.createElement('div');

            if (fret === 1) {
                frets_row.className = 'row first';
            } else if (fret === first_fret + 4) {
                frets_row.className = 'row last';
            } else {
                frets_row.className = 'row';
            }

            barre_start = -1;
            barre_finish = -1;
            barre_finger = -1;

            if (footer_row_needed) {
                for (i = 0; i < num_strings; i += 1) {
                    if (barre_start !== -1) {
                        if (frets[i] === fret && fingers[i] === barre_finger) {
                            barre_finish = i;
                        } else if (frets[i] < fret || (frets[i] === fret && fingers[i] !== barre_finger)) {
                            if (barre_finish !== -1) {
                                break; // exiting
                            }
                            barre_start = -1; // resetting
                        }
                    }

                    if (barre_start === -1 && fingers[i] !== -1 && frets[i] === fret) {
                        barre_start = i;
                        barre_finger = fingers[i];
                    }
                }

                if (barre_finish <= barre_start) {
                    barre_start = -1;
                }
            }

            for (i = 0; i < num_strings - 1; i += 1) {
                fret_cell = document.createElement('div');

                if (i === barre_start) {
                    barre_cell = document.createElement('div');
                    barre_cell.className = 'barre barre-' + (barre_finish - barre_start);

                    fret_cell.appendChild(barre_cell);
                } else if (i < barre_start || i >= barre_finish) {
                    if (i !== barre_finish && frets[i] === fret) {
                        knob_cell = document.createElement('div');
                        knob_cell.className = 'knob';

                        fret_cell.appendChild(knob_cell);
                    }

                    if (i === num_strings - 2 && frets[num_strings - 1] === fret) {
                        knob_cell = document.createElement('div');
                        knob_cell.className = 'knob right';

                        fret_cell.appendChild(knob_cell);
                    }
                }

                frets_row.appendChild(fret_cell);
            }

            if (fret === first_fret && fret !== 1) {
                fretno_cell = document.createElement('div');
                fretno_cell.className = 'fretno';
                fretno_cell.innerHTML = fret;

                frets_row.appendChild(fretno_cell);
            }

            container.appendChild(frets_row);
        }

        if (footer_row_needed) {
            container.appendChild(build_footer(frets, fingers));
        }

        return container;

    };

    module.on_load = function () {
        return module.replace_tags();
    };

    module.replace_tags = function (container, classname, tagname) {

        // default arguments
        if (container === undefined) {
            container = document.body;
        }
        if (classname === undefined) {
            classname = 'chord-diagram';
        }
        if (tagname === undefined) {
            tagname = 'div';
        }

        var diagram_tags = container.getElementsByClassName(classname),
            j,
            diagram_number,
            diagram_tag,
            shift,
            frets,
            frets_string,
            frets_number,
            fret_char,
            fingers,
            fingers_string,
            finger_char,
            diagram;

        diagram_number = diagram_tags.length;
        for (j = 0; j < diagram_number; j += 1) {

            diagram_tag = diagram_tags[j];
            if (typeof diagram_tag === 'object') {

                frets_string = diagram_tag.getAttribute('data-frets');
                if (frets_string) {

                    shift = +diagram_tag.getAttribute('data-shift');
                    frets_number = frets_string.length;
                    frets = [];

                    for (i = 0; i < frets_number; i += 1) {
                        fret_char = frets_string.charAt(i).toLowerCase();
                        if (fret_char === 'x') {
                            frets[i] = -1;
                        } else {
                            frets[i] = +fret_char + shift;
                        }
                    }

                    fingers_string = diagram_tag.getAttribute('data-fingers');
                    if (fingers_string && frets_number <= fingers_string.length) {
                        fingers = [];
                        for (i = 0; i < frets_number; i += 1) {
                            finger_char = fingers_string.charAt(i).toLowerCase();
                            if (finger_char === 'x') {
                                fingers[i] = -1;
                            } else {
                                fingers[i] = +finger_char;
                            }
                        }
                        diagram = module.build_diagram(frets, fingers);
                    } else {
                        diagram = module.build_diagram(frets);
                    }

                    diagram_tag.innerHTML = diagram.innerHTML;
                }
            }
        }
    };

    return module;
}());


/*
//Code example to load it automatically:
if (window.jQuery) {
    window.jQuery.ready(chordDiagram.on_load);
} else {
    var oldonload = window.onload;
    if (typeof window.onload !== 'function') {
        window.onload = chordDiagram.on_load;
    } else {
        window.onload = function () {
            if (oldonload) {
                oldonload();
            }
            chordDiagram.on_load();
        };
    }
}
// */
