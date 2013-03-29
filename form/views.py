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
    print session, request.user
    if request.user.is_anonymous:
        formularies = db.formularies.find().limit(4)
        return render_template('marketing.html',
                               formularies=formularies)

    formularies = db.formularies.find({'owner': request.user.username})
    drugs = db.drugs.find().limit(10)
    return render_template('index.html',
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
    return render_template('about.html')
