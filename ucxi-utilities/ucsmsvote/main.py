#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


class Vote(db.Model):
    phoneNumber = db.StringProperty(required=True)
    createdAt   = db.DateTimeProperty()




class VoteHandler(webapp.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain; charset="iso-8859-1"'

        phone       = self.request.get('msisdn')
        msg         = self.request.get('message')
        words       = msg.split()

        if len(words) < 4:
            self.response.out.write('Du, nu fattar jag inte alls vad du menar!')
            return

        shortname   = words[2]
        oid         = words[3]

        poll = db.get(db.Key.from_path('Poll', shortname))
        if not poll:
            reply = u'Hur stavar du egentligen? Jag hittar ingen tävling som kallas ' + shortname
            self.response.out.write(reply.encode('iso-8859-1'))
            return

        option = db.get(db.Key.from_path('Poll', shortname, 'Option', oid))
        if not option:
            reply = u'Hördu, det verkar inte finnas nåt bidrag som kallas ' + oid
            self.response.out.write(reply.encode('iso-8859-1'))
            return

        vote = Vote.all().ancestor(poll).filter('phoneNumber =', phone)
        if vote:
            reply = u'Nä du, mig lurar du inte! Du har redan röstat i den här tävlingen!'
            self.response.out.write(reply.encode('iso-8859-1'))
            return

        vote = Vote(parent=option, phoneNumber=phone, createdAt=datetime.datetime.now())

        reply = u'Tack för din röst på ' + option.name + u' i ' + poll.name + u'!'
        self.response.out.write(reply.encode('iso-8859-1'))



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
        sort        = self.request.get('sortbyvotes')
        polls       = Poll.all()
        if shortname:
            polls.ancestor(db.Key.from_path('Poll', shortname))

        out = {}
        for p in polls:
            options = []
            oq      = Option.all().ancestor(p).order('oid')
            for o in oq:
                votes = Vote.all().ancestor(o).count()
                options.append({'id': o.oid, 'name': o.name, 'votes': votes})

            out[p.key().name()] = options if (not sort or sort == '0') else sorted(options, lambda opts: opts['votes'])

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

        option = Option(oid=oid, name=name, createdAt=datetime.datetime.now(), parent=poll.key())
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

