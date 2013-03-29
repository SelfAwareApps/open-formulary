"""
Users for Open Formulary
"""
from urllib import urlencode

from bson.objectid import ObjectId
from flask import Blueprint, request, redirect, session, current_app, _request_ctx_stack
from lxml import etree
import requests

import pycas, settings
from db import db

api = Blueprint('users', __name__)


class User(object):
    """
    Our User class for use with the Flask Login extension
    and other helpful stuffs!
    """

    def __init__(self, document=None, authenticated=False):
        self.document      = document
        self._is_auth      = authenticated
        return

    def __str__(self):
        username, klass = '', 'AnonymousUser'
        if self.is_authenticated:
            klass = 'User'
            username = self.document['username']
        return '<{klass} {username}>'.format(klass=klass, username=username)

    @staticmethod
    def get_or_create(username, authenticated=False):
        """
        Given a username, return an instantiated User object.

        If the user was not previously in the database, create
        them now.
        """
        print 'Get or create for', username, authenticated
        document = db.users.find_one({'username': username})
        if document is not None:
            return User(document=document, authenticated=authenticated)

        userdoc = dict(username=username)
        userid = db.users.insert(userdoc)
        userdoc['_id'] = userid
        return User(document=userdoc, authenticated=authenticated)

    @staticmethod
    def from_userid(userid, authenticated=False):
        """
        Given the unicode ID of a user, return the user object. or None
        """
        document = db.users.find_one({'_id': ObjectId(userid)})
        if document is None:
            return None
        return User(document=document, authenticated=authenticated)

    @staticmethod
    def authenticate(ticket=None, service=None):
        """
        Ask our CAS server whether this user is authenticated please.

        If the ticket is invalid (expired etc) return None.
        """
        params = dict(ticket=ticket, service=service)
        authurl = '{0}/proxyValidate?{1}'.format(settings.CAS_SERVER, urlencode(params))
        resp = requests.get(authurl)
        if resp.status_code != 200:
            return
        # Strip the namespace - sloppy...
        root = etree.fromstring(resp.content.replace('cas:', ''))
        fail = root.find('authenticationFailure')
        if fail:
            return
        username = root.find('authenticationSuccess/user').text
        print username, 'Authenticated with CAS'
        return User.get_or_create(username, authenticated=True)

    @property
    def userid(self):
        """
        Return a unicode version of this user's ID.
        """
        if self.document is None:
            return None
        return unicode(self.document['_id'])

    @property
    def username(self):
        """
        Return a unicode version of this user's username.
        """
        if self.document is None:
            return None
        return unicode(self.document['username'])

    @property
    def is_authenticated(self):
        """
        Predicate function to determine whether this user is
        logged in or not.
        """
        return self._is_auth

    @property
    def is_active(self):
        """
        Predicate function to determine whether we have suspended
        this user for some reason?

        (Currently no use case for this, just an Interface reqiurement)
        """
        return True

    @property
    def is_anonymous(self):
        """
        Predicate function to determine whether this user is anonymous.
        """
        if self.document is None:
            return True
        return False


def login_user(user):
    """
    Log in USER
    """
    session['user_id'] = user.userid
    return True

def logout_user():
    """
    Log a user out
    """
    if 'user_id' in session:
        del session['user_id']
    return True

def load_user():
    """
    Load a user from the current request.

    If the request id for static media, return a dummy user
    else load a user from the cookie.
    """
    context = _request_ctx_stack.top
    if request.path.startswith(current_app.static_url_path):
        # load up an anonymous user for static pages
        request.user = User()
        return
    if 'user_id' not in session:
        request.user = User()
        return
    user = User.from_userid(session['user_id'], authenticated=True)
    if user is not None:
        request.user = user
        return
    logout_user()
    request.user = User()
    return


@api.route('/login')
def login():
    """
    Log our user in
    """
    cas_url = '{0}/login?service={1}'.format(settings.CAS_SERVER, request.url)
    ticket = request.args.get('ticket', None)
    if ticket is None:
        return redirect(cas_url)

    user = User.authenticate(ticket=ticket, service=request.url)
    if user is None:
        return redirect(cas_url)

    login_succ = login_user(user)
    return redirect('/')

@api.route('/logout')
def logout():
    """
    Log our user out

    Return: Http Response
    Exceptions: None
    """
    if request.user.is_authenticated:
        logout_user()
        cas_url = '{0}/logout?url=http://{1}'.format(settings.CAS_SERVER, request.host)
        return redirect(cas_url)
    return redirect('/')


def setup(app):
    """
    Set up the authentication
    """
    app.before_request(load_user)
