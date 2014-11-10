#!/usr/bin/env python
# Copyright(C) 2012 thomasv@gitorious

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/agpl.html>.
"""
sessions are identified with cookies
 - each session has a buffer of responses to requests


from the processor point of view:
 - the user only defines process() ; the rest is session management.  thus sessions should not belong to processor

"""
import json
import time
from Cookie import SimpleCookie
import gevent
from gevent.queue import Queue
from gevent.pywsgi import WSGIServer

from .processor import Session
from .utils import random_string, print_log


class HttpSession(Session):

    def __init__(self, dispatcher, ssl_enabled, session_id):
        Session.__init__(self, dispatcher)
        self.address = session_id
        self.name = "HTTP" if not ssl_enabled else "HTTPS"
        self.timeout = 60
        self.response_queue = Queue()
        self.dispatcher.add_session(self)

    def send_response(self, response):
        try:
            msg = json.dumps(response)
        except BaseException as e:
            logger.error('send_response:' + str(e))
        else:
            self.response_queue.put(msg)


class HttpServer(WSGIServer):

    def __init__(self, dispatcher, listener, **ssl_args):
        WSGIServer.__init__(self, listener, self._application, None, 'default', 'default', None, None, **ssl_args)
        self.shared = dispatcher.shared
        self.dispatcher = dispatcher.request_dispatcher
        self.host = listener[0]
        self.port = listener[1]

    def start(self):
        WSGIServer.start(self)
        print_log(("HTTPS" if self.ssl_enabled else "HTTP") + " server started on port %d" % self.port)

    def create_session(self):
        session_id = random_string(20)
        HttpSession(self.dispatcher, self.ssl_enabled, session_id)
        return session_id

    def handle_data(self, data, session):
        try:
            request = json.loads(data)
        except:
            session.send_response({"error": "bad JSON"})
            return

        session.time = time.time()

        if not isinstance(request, list):
            request = [request]

        for command in request:
            if 'id' in command and 'method' in command:
                if command['method'] == 'server.stop':
                    return session.send_response({'result': 'ok'})
                else:
                    self.dispatcher.push_request(session, command)
            else:
                session.send_response({"error": "syntax error", "request": command})

    def _application(self, env, start_response):
        method = env['REQUEST_METHOD']
        if method == 'OPTIONS':
            start_response('200 OK', [('Allow', 'GET, POST, OPTIONS'),
                                      ('Access-Control-Allow-Origin', '*'),
                                      ('Access-Control-Allow-Headers', 'Cache-Control, Content-Language, Content-Type, Expires, Last-Modified, Pragma, Accept-Language, Accept, Origin'),
                                      ('Content-Length', '0')])
            return []
        elif method == 'GET' or method == 'POST':
            session_id = None
            response = []
            try:
                if 'HTTP_COOKIE' in env:
                    cookie = SimpleCookie(env['HTTP_COOKIE'])
                    if 'SESSION' in cookie:
                        session_id = cookie['SESSION'].value

                if session_id is None:
                    session_id = self.create_session()

                session = self.dispatcher.get_session_by_address(session_id)
                if session:
                    if method == 'POST':
                        data = env['wsgi.input'].read().strip()
                        self.handle_data(data, session)

                    status = '200 OK'
                    gevent.sleep(0.01)
                    while not session.response_queue.empty():
                        response.append(session.response_queue.get())
                else:
                    status = '500 Internal Server Error'
                    response.append(json.dumps({"error": "session not found"}))
            except:
                status = '500 Internal Server Error'

            start_response(status, [("Set-Cookie", "SESSION=%s" % session_id),
                                    ("Content-type", "application/json-rpc"),
                                    ("Access-Control-Allow-Origin", "*")])
            return response
        else:
            start_response('501 Not Implemented', [])
            return []
