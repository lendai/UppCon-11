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
    name            = db.StringProperty(required=True)
    isClosed        = db.BooleanProperty()
    singleVote      = db.BooleanProperty()
    createdAt       = db.DateTimeProperty()


class Option(db.Model):
    oid         = db.StringProperty(required=True)
    externalId  = db.IntegerProperty()
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

        shortname   = words[2].lower()
        oid         = words[3].lower()

        if oid.isdigit():
            oid = str(int(oid));

        poll = db.get(db.Key.from_path('Poll', shortname))
        if not poll:
            reply = u'Jag tror du är på fel konvent. Hittar ingen tävling som kallas ' + shortname
            logging.warning("Invalid shortname: " + shortname)
            self.response.out.write(reply.encode('iso-8859-1'))
            return

        if poll.isClosed:
            reply = u'Tyvärr, omröstningen för ' + poll.name + u' är stängd.'
            logging.warning("Attempt to vote in closed poll " + shortname)
            self.response.out.write(reply.encode('iso-8859-1'))
            return

        option = Option.all().ancestor(poll).filter('oid =', oid).get()
        if not option:
            reply = u'Nu skrev du nog fel, jag hittar inget bidrag som kallas ' + oid
            logging.warning("Invalid option: " + oid + " (shortname: " + shortname + ")")
            self.response.out.write(reply.encode('iso-8859-1'))
            return

        vote = Vote.all().ancestor(poll).filter('phoneNumber =', phone).get()
        if vote and poll.singleVote:
            reply = u'Nä du, mig lurar du inte! Du har redan röstat i den här tävlingen!'
            logging.warning("Attempt to vote more than once from number " + phone)
            self.response.out.write(reply.encode('iso-8859-1'))
            return

        vote = Vote(parent=option, phoneNumber=phone, createdAt=datetime.datetime.now())
        vote.put()
        logging.info("vote in " + shortname + " for " + oid + " registered")

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
        shortname   = self.request.get('shortname').lower()

        if name == '' or shortname == '':
            self.response.out.write(json.dumps({'status': "invalid name or shortname"}))
            self.response.set_status(404)
            return

        #lax = Poll.all()
        #for p in lax:
        #    p.isClosed=False
        #    p.singleVote=False
        #    p.put()

        poll = db.get(db.Key.from_path('Poll', shortname))
        if poll != None:
            self.response.out.write(json.dumps({'status': 'shortname already exists'}))
            self.response.set_status(403)
            return

        poll = Poll(key_name=shortname, isClosed=False, singleVote=False, name=name, createdAt=datetime.datetime.now())
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
        shortname   = self.request.get('shortname').lower()
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

            if not sort or sort == '0':
                out[p.key().name()] = options
            else:
                sortedlist = sorted(options, key=lambda opts: opts['votes'])
                sortedlist.reverse()
                out[p.key().name()] = sortedlist

        self.response.out.write(json.dumps(out))


    def post(self):
        shortname   = self.request.get('shortname').lower()
        oid         = self.request.get('id').lower()
        eid         = self.request.get('external_id')
        name        = self.request.get('name')

        if oid.isdigit():
            oid = str(int(oid))

        if not eid:
            eid = None
        else:
            eid = int(eid)

        poll = db.get(db.Key.from_path('Poll', shortname))
        if not poll:
            self.response.out.write(json.dumps({'status': 'no such poll'}))
            self.response.set_status(404)
            return

        option = Option.all().ancestor(poll).filter('oid =', oid).get()
        if option:
            self.response.out.write(json.dumps({'status': 'id already exists for this poll'}))
            self.response.set_status(403)
            return

        option = Option(oid=oid, externalId=eid, name=name, createdAt=datetime.datetime.now(), parent=poll.key())
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

