"""
Our formulary classes
"""
import collections

from bson.objectid import ObjectId
from flask import request

from db import db

class Field(object):
    def __init__(self, default=None, key=None):
        self.default = default
        self.name = None
        self.key = None

    def __get__(self, instance, owner):
        key = self.key or self.name
        docitem = instance._document.get(key, None)
        if docitem:
            return docitem
        return self.default

    def __set__(self, instance, value):
        instance._document[self.name] = value
        return

    def set_name(self, name):
        """
        Set the name
        """
        self.name = name


class CharField(Field):
    pass

class BoolField(Field):
    pass

class ListField(Field):
    def __init__(self, default=[], key=None):
        super(ListField, self).__init__(default=default, key=key)

class IntField(Field):
    pass

class DictField(Field):
    pass

class MongModelMeta(type):
    def __new__(meta, class_name, bases, new_attrs):
        cls = type.__new__(meta, class_name, bases, new_attrs)
        cls.fields = set()
        for name, value in new_attrs.items():
            if isinstance(value, Field):
                value.set_name(name)
                cls.fields.add(name)
        return cls

class MongModel(object):
    """
    Mongodb base model.
    """
    __metaclass__ = MongModelMeta
    collection = None

    def __init__(self, **kwargs):
        """
        Attr assignin'
        """
        self._document = kwargs

    def __getitem__(self, item):
        """
        Check the document frist, then Super.
        """
        if item in self.fields:
            return getattr(self, item)

        if item in self._document:
            return self._document[item]
        return super(Formulary, self).__getitem__(item)

    @classmethod
    def get(klass, instanceid):
        """
        Return an instance from it's id

        Arguments:
        - `instanceid`: str

        Return: dict or None
        Exceptions: None
        """
        params = klass.collection.find_one({'_id': ObjectId(instanceid)})
        if params is not None:
            return klass(**params)
        return None

    @classmethod
    def get_or_create(klass, **kwargs):
        """
        Given a username, return an instantiated User object.

        If the user was not previously in the database, create
        them now.
        """
        document = klass.collection.find_one(kwargs)
        doc = kwargs.copy()

        if document is None:
            userid = klass.collection.insert(kwargs)
            doc['_id'] = userid
        else:
            doc.update(document)

        print 'get or create', doc
        return klass(**doc)

    def save(self):
        """
        Save this formulary to the database

        Arguments:
        - `formulary`: dict

        Return: None
        Exceptions: None
        """
        objid = self.collection.save(self._document)
        if '_id' not in self._document:
            self._document['_id'] = objid
        return


class Formulary(MongModel):
    """
    Our base formulary class for API convenience.
    """
    collection = db.formularies

    name            = CharField()
    description     = CharField()
    public          = BoolField(default=True)
    owner           = CharField()
    codes           = ListField()
    following_count = IntField(default=0)

    def __str__(self):
        return '<Formulary {0} ({1})>'.format(self.name, self.owner)

    @staticmethod
    def validate_formulary(form):
        """
        Given FORM, a dict of POST params, validate that they meet our
        requirements for a minimally sane formulary.

        Return: errs, data
        Exceptions: None
        """
        errs = []
        # Extract the metadata
        name, public = request.form['name'], request.form.get('public', None) == 'on'
        description = request.form['description']
        owner = request.user.username

        # Parse the codes we get sent from checkboxes
        codes = [c for c in request.form.keys() if c[0] in ['0', '1']]

        itemdict = collections.defaultdict(lambda: collections.defaultdict(list))
        for code in codes:
            itemdict[code[:2]][code[2:4]].append(code)

        data = dict(name=name, public=public, description=description, owner=owner,
                    codes=itemdict)

        if name == '':
            errs.append('Formularies must have a name')
        if description == '':
            errs.append('Formularies must have a description')

        return errs, data

    @classmethod
    def popular(klass, num):
        """
        Return the NUM most popular formularies

        Arguments:
        - `num`: int

        Return: Mongodb Cursor
        Exceptions: None
        """
        return [Formulary(**f) for f in
                db.formularies.find({'public': True}).sort('following_count').limit(num)]



if __name__ == '__main__':
    frm = Formulary(name='My Frist Formulary')
    print frm
    print frm.name, frm.public
