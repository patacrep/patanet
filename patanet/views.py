# -*- coding: utf-8 -*-
#    Copyright (C) 2014 The Patacrep Team
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A view to change the current language"""

from django.shortcuts import redirect


def setlang(request):
    lang = request.REQUEST.get("lang", "")
    next_url = request.REQUEST.get("next", "/")
    if lang=="":
        return redirect(next_url)
    next_path = "/".join(next_url.split('/')[2:])
    return redirect("/" + lang + "/" + next_path)
