"""
Views for open formulary
"""
import collections

from bson.objectid import ObjectId
from flask import (Blueprint, abort, flash, session, request, redirect,
                   render_template, url_for)

from db import db
import bnf, errors
from models import Formulary
from users import login_required

blue = Blueprint('views', __name__)

@blue.route('/')
def index():
    """
    If the user isn't logged in, show them a marketing page
    explaining what the service does.

    If we're logged in, show them their formularies.
    """
    if not request.user.is_authenticated:
        popular = Formulary.popular(4)
        return render_template('marketing.jinja2',
                               popular=popular)

    formularies = db.formularies.find({'owner': request.user.username})
    following_ids = request.user.following
    following = db.formularies.find({'_id': {'$in': [ObjectId(i) for i in following_ids]}})
    return render_template('index.jinja2',
                           formularies=formularies,
                           following=following)

@blue.route('/about')
def about():
    return render_template('about.html')

@blue.route('/create', methods=['GET', 'POST'])
@login_required
def formulary_create():
    """
    Create a new formulary.

    Return: Http response
    Exceptions: None
    """
#    chapters, sections, paras = bnf.get_structure()
    errs, data = [], {}
    if request.method == 'POST':
        errs, data = Formulary.validate_formulary(request.form)
        # As we're creating here, we perform extra validation to ensure name uniqueness
        formulary = db.formularies.find_one({'name': data['name'], 'owner': data['owner']})
        if formulary:
            errs.append('Formulary names must be unique')

        if not errs:
            oid = unicode(db.formularies.save(data))
            return redirect(url_for('views.formulary_detail', formid=oid))

    return render_template('create.formulary.jinja2',
                           errors=errs,
                           walk=bnf.walk,
                           formdata=data)


@blue.route('/formulary/<formid>')
def formulary_detail(formid):
    """
    Render the detail for the formulary


    Arguments:
    - `formulary_id`:

    Return:
    Exceptions:
    """
    formulary = Formulary.get(formid)
    chapters, sections, paras = bnf.get_structure(raw=True)
    drugs = dict([(d['code'], d) for d in  db.drugs.find()])
    following = False
    if request.user.is_authenticated:
        following = formid in request.user.following
    return render_template('detail.formulary.jinja2',
                           chapters=chapters,
                           sections=sections,
                           paras=paras,
                           drugs=drugs,
                           following=following,
                           formulary=formulary,
                           formid=formid)


@blue.route('/formulary/<formid>/delete', methods=['GET', 'POST'])
@login_required
def formulary_delete(formid):
    """
    Delete this formulary

    Arguments:
    - `formid`: str id of the formulary

    Return: HttpResponse
    Exceptions: None
    """
    formulary = db.formularies.find_one({'_id': ObjectId(formid)})
    name = formulary['name']
    if request.method == 'POST':
        db.formularies.remove(formulary)
        flash('You deleted {0}'.format(name))
        return redirect('/')
    return render_template('delete.formulary.jinja2', formulary=formulary)


@blue.route('/formulary/<formid>/edit', methods=['GET', 'POST'])
@login_required
def formulary_edit(formid):
    """
    Edit a particular formulary


    Arguments:
    - `formid`: str id of the formulary we're editing

    Return: Http Response
    Exceptions: None
    """
    formulary = db.formularies.find_one({'_id': ObjectId(formid)})
    print formulary
    if formulary['owner'] != request.user.username:
        abort(401)

    errs = []
    if request.method == 'POST':
        errs, data = Formulary.validate_formulary(request.form)
        if not errs:
            formulary.update(data)
            db.formularies.save(formulary)
            target = url_for('views.formulary_detail',
                             formid=unicode(formulary['_id'])
                             )
            return redirect(target)

    return render_template('edit.formulary.jinja2',
                           errs=errs,
                           walk=bnf.walk,
                           formulary=formulary,
                           formdata=formulary)


@blue.route('/formulary/<formid>/follow', methods=['POST', 'GET'])
@login_required
def formulary_follow(formid):
    """
    Given a Formulary id, add this formulary to the user's
    followed formularies.

    Arguments:
    - `formid`: str id of the formulary

    Return: Http Response
    Exceptions: None
    """
    backto_detail = redirect(url_for('views.formulary_detail', formid=formid))

    if request.method == 'GET':
        return backto_detail

    user, formulary = request.user, Formulary.get(formid)

    if formulary['owner'] == user.username:
        return backto_detail

    if 'following' not in user.document:
        user.document['following'] = []
    if 'following_count' not in formulary:
        formulary['following_count'] = 0

    if formid in user.document['following']:
        user.document['following'].remove(formid)
        formulary['following_count'] -= 1
    else:
        user.document['following'].append(formid)
        formulary['following_count'] += 1

    user.save()
    save_formulary(formulary)
    return backto_detail



@blue.route('/user/<username>')
def formulary_userlist(username):
    """
    List the formularies owned by this user


    Arguments:
    - `username`: str username of the formulary

    Return: Http response
    Exceptions: None
    """
    formularies = db.formularies.find({'owner': username, 'public': True})
    return render_template('list.user.formulary.jinja2',
                           formularies=formularies,
                           username=username)

@blue.route('/formulary/list')
def formulary_list():
    """
    List all formularies.

    Return: HttpResponse
    Exceptions: None
    """
    return render_template('list.formulary.jinja2', popular=Formulary.popular(10))
