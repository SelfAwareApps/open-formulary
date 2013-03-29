"""
Main Flask application object
"""
from flask import (Flask, abort, request, redirect, Response, make_response,
                   session, url_for)
from flask import render_template
#import flask_login as login
import jinja2
from jinja2 import evalcontextfilter, Markup, escape

from db import db
import settings, users, views
from mongsession import MongoSessionInterface

app = Flask(__name__)
app.debug = True
app.session_interface = MongoSessionInterface(db)
app.register_blueprint(views.blue)
app.register_blueprint(users.api)
users.setup(app)

# def include_file(name):
#     return jinja2.Markup(loader.get_source(env, name)[0])

# loader = jinja2.PackageLoader(__name__, 'templates')
# env = jinja2.Environment(loader=loader)
# env.globals['include_file'] = include_file
# env.globals['url_for'] = url_for
