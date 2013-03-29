import pickle
from datetime import timedelta
from uuid import uuid4
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin


class MongoSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class MongoSessionInterface(SessionInterface):
    serializer = pickle
    session_class = MongoSession

    def __init__(self, mongo, prefix='session:'):
        self.mongo = mongo
        self.coll  = getattr(mongo, prefix)

    def generate_sid(self):
        return str(uuid4())

    def get_mongo_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def _get_mongo_session(self, sid):
        """
        Return the mongodb session document or None
        """
        return self.coll.find_one({'sid': sid})

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid)
        monger = self._get_mongo_session(sid)
        if monger is not None:
            data = self.serializer.loads(monger['data'])
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.coll.remove({'sid': session.sid})
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        mongo_exp = self.get_mongo_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        monger = self._get_mongo_session(session.sid)
        if monger is None:
            monger = {'sid': session.sid}

        monger['data'] = val
        monger['expiry'] = int(mongo_exp.total_seconds())
        self.coll.save(monger)

        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True,
                            domain=domain)
