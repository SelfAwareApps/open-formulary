"""
Users for Open Formulary
"""
import functools
from urllib import urlencode

from bson.objectid import ObjectId
from flask import (Blueprint, request, redirect, session, current_app,
                   _request_ctx_stack, url_for)
from lxml import etree
import requests

import models, pycas, settings
from db import db

__all__ = [
    'views',
    'User',
    'login_required',
    'setup',
    'OFUser'
]

views = Blueprint('users.views', __name__)
ActiveUserKlass = None

class User(models.MongModel):
    """
    Our User class for use with the Flask Login extension
    and other helpful stuffs!
    """
    collection = db.users

    username = models.CharField()
    userid   = models.CharField(key='_id')

    def __init__(self, authenticated=False, **kwargs):
        """
        Pluck authentication details from the Mongo Model args

        Arguments:
        - `authenticated`: bool - whether this User is authenticated
        - `**kwargs`: dict

        Return: None
        Exceptions: None
        """
        self._authenticated = authenticated
        super(User, self).__init__(**kwargs)


    def __str__(self):
        username, klass = '', 'AnonymousUser'
        if self.authenticated:
            klass = 'User'
            username = self.document['username']
        return '<{klass} {username}>'.format(klass=klass, username=username)

    @classmethod
    def authenticate(klass, ticket=None, service=None):
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
        return klass.get_or_create(username=username, authenticated=True)

    @property
    def is_authenticated(self):
        """
        Predicate function to determine whether this user is
        logged in or not.
        """
        return self._authenticated




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
        request.user = ActiveUserKlass()
        return
    if 'user_id' not in session: # Then we're anonymous
        request.user = ActiveUserKlass()
        return
    user = ActiveUserKlass.get(session['user_id'])
    if user is not None:
        user._authenticated = True
        request.user = user
        return
    logout_user()
    request.user = ActiveUserKlass()
    return


@views.route('/login')
def login():
    """
    Log our user in
    """
    cas_url = '{0}/login?service={1}'.format(settings.CAS_SERVER, request.url)
    ticket = request.args.get('ticket', None)
    next_page = request.args.get('next_page', None)
    if ticket is None:
        return redirect(cas_url)

    user = ActiveUserKlass.authenticate(ticket=ticket, service=request.url)
    if user is None:
        return redirect(cas_url)

    login_succ = login_user(user)
    if next_page:
        return redirect(next_page)
    return redirect('/')

@views.route('/logout')
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

def login_required(fn):
    """
    Wrap a view FN such that the user must log in
    before viewing it.

    Arguments:
    - `fn`: callable

    Return: callable
    Exceptions: None
    """
    @functools.wraps(fn)
    def check_auth(*args, **kwargs):
        """
        Check to see whether the current user is logged in or not

        Return: http response
        Exceptions: None
        """
        if request.user.is_authenticated:
            return fn(*args, **kwargs)
        print 'redirecting in decorator'
        return redirect(url_for('users.login', next_page=request.path))

    return check_auth



def setup(app, userklass=User):
    """
    Set up the authentication
    """
    app.before_request(load_user)
    global ActiveUserKlass
    ActiveUserKlass = userklass


class OFUser(User):
    """
    Extra User attributes as required by the Open Formulary application
    """
    collection = db.users

    following = models.ListField(default=[])
