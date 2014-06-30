# Copyright: 2014 Dennis Schmalacker <github@progde.de>
# License: BSD 2-clause, see LICENSE for details.

import errno

from flask import current_app, redirect, url_for, render_template, abort
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from . import blueprint
from ..utils.permissions import *


class DeleteView(MethodView):
    def get(self, name):
        if not may(DELETE):
            abort(403)
        try:
            with current_app.storage.open(name) as item:
                if item.meta['locked']:
                    error = 'File locked.'
                elif not item.meta['complete']:
                    error = 'Upload incomplete. Try again later.'
                else:
                    error = None
                if error:
                    return render_template('display_error.html', name=name, item=item, error=error), 409

            current_app.storage.remove(name)

        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return render_template('file_not_found.html'), 404
            raise

        return redirect(url_for('bepasty.display', name=name))


blueprint.add_url_rule('/<itemname:name>/+delete', view_func=DeleteView.as_view('delete'))
