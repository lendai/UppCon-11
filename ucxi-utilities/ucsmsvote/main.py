#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from django.utils import simplejson as json
import random
import time
import datetime
import logging


class Poll(db.Model):
    name        = db.StringProperty(required=True)
    createdAt   = db.DateTimeProperty()


class Option(db.Model):
    oid         = db.StringProperty(required=True)
    name        = db.StringProperty(required=True)
    createdAt   = db.DateTimeProperty()



class VoteHandler(webapp.RequestHandler):
    def post(self):
        self.response.out.write('lax')


class PollHandler(webapp.RequestHandler):
    def get(self):
        out = []
        for p in Poll.all():
            out.append({'shortname': p.key().name(), 'name': p.name})

        self.response.out.write(json.dumps(out))


    def post(self):
        name        = self.request.get('name')
        shortname   = self.request.get('shortname')

        if name == '' or shortname == '':
            self.response.out.write(json.dumps({'status': "invalid name or shortname"}))
            self.response.set_status(404)
            return

        poll = db.get(db.Key.from_path('Poll', shortname))
        if poll != None:
            self.response.out.write(json.dumps({'status': 'shortname already exists'}))
            self.response.set_status(403)
            return

        poll = Poll(key_name=shortname, name=name, createdAt=datetime.datetime.now())
        poll.put()

        self.response.out.write(json.dumps({'status': 'ok'}))


    def delete(self, shortname):
        poll = db.get(db.Key.from_path('Poll', shortname))
        if poll == None:
            self.response.set_status(404)
            return

        poll.delete()
        self.response.out.write(json.dumps({'status': 'ok'}))



class OptionHandler(webapp.RequestHandler):
    def get(self):
        shortname   = self.request.get('shortname')
        polls       = Poll.all()
        if shortname:
            polls.ancestor(db.Key.from_path('Poll', shortname))

        out = {}
        for p in polls:
            options = {}
            for o in Option.all().ancestor(p.key()):
                options[o.oid] = {'name': o.name}
            out[p.key().name()]

        self.response.out.write(json.dumps(out))


    def post(self):
        shortname   = self.request.get('shortname')
        oid         = self.request.get('id')
        name        = self.request.get('name')

        poll = db.get(db.Key.from_path('Poll', shortname))
        if not poll:
            self.response.out.write(json.dumps({'status': 'no such poll'}))
            self.response.set_status(404)
            return

        option = Option(oid=oid, name=name, parent=poll.key())
        option.put()

        self.response.out.write(json.dumps({'status': 'ok'}))


    def delete(self, shortname, oid):
        o = Option.all().ancestor(db.Key.from_path('Poll', shortname)).filter('oid =', oid).get()
        if not o:
            self.response.out.write(json.dumps({'status': 'no such option'}))
            self.response.set_status(404)
            return

        o.delete()
        self.response.out.write(json.dumps({'status': 'ok'}))




def main():
    application = webapp.WSGIApplication([('/vote', VoteHandler),
                                          ('/poll', PollHandler),
                                          ('/poll/(\w+)', PollHandler),
                                          ('/option', OptionHandler),
                                          ('/option/(\w+)/([\w\d]+)', OptionHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

