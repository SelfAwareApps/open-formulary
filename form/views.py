"""
Views for open formulary
"""
from flask import Blueprint, session, request, render_template

from db import db

blue = Blueprint('views', __name__)

@blue.route('/')
def index():
    """
    If the user isn't logged in, show them a marketing page
    explaining what the service does.

    If we're logged in, show them their formularies.
    """
    if request.user.is_anonymous:
        formularies = db.formularies.find().limit(4)
        return render_template('marketing.jinja2',
                               formularies=formularies)

    formularies = db.formularies.find({'owner': request.user.username})
    drugs = db.drugs.find().limit(10)
    return render_template('index.jinja2',
                           formularies=formularies,
                           drugs=drugs)

@blue.route('/about')
def about():
    return render_template('about.html')

@blue.route('/create')
def create():
    """
    Create a new formulary.

    Return: Http response
    Exceptions: None
    """
    chapters = db.struct.find({'level': 'chapter'}).sort('chapter')
    return render_template('create.jinja2', chapters=chapters)
