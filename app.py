"""
Open Formulary
"""
from flask import Flask, abort, request, redirect, Response, make_response
from flask import render_template
import flask_login
import jinja2
from jinja2 import evalcontextfilter, Markup, escape
from pymongo.objectid import ObjectId

from db import db

app = Flask(__name__)
app.debug = True

login_manager = flask_login.LoginManager()
login_manager.login_view = 'login'

class User(object):
    """
    Our User class for use with the Flask Login extension
    and other helpful stuffs!
    """

    def __init__(self, document=None):
        self.document = document
        return

    def is_authenticated(self):
        """
        Predicate function to determine whether this user is
        logged in or not.
        """
        return False

    def is_active(self):
        """
        Predicate function to determine whether we have suspended
        this user for some reason?

        (Currently no use case for this, just an Interface reqiurement)
        """
        return True

    def is_anonymous(self):
        """
        Predicate function to determine whether this user is anonymous.
        """
        if self.document is None:
            return True
        return False

    def get_id(self):
        """
        Return a unicode version of this user's ID.
        """
        if self.document is None:
            return None
        return unicode(self.document['_id'])


@login_manager.user_loader
def get_user(userid):
    """
    Given the unicode ID of a user, return the user object.
    """
    return User(document=db.users.find_one({'_id': ObjectId(userid)}))


def include_file(name):
    return jinja2.Markup(loader.get_source(env, name)[0])

loader = jinja2.PackageLoader(__name__, 'templates')
env = jinja2.Environment(loader=loader)
env.globals['include_file'] = include_file

"""
Views
"""
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    next_page = request.host

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
