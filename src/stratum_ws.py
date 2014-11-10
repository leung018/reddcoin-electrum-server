import json
import time
import gevent
from gevent import Greenlet
from gevent.queue import Queue
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

from .processor import Session
from .utils import print_log


class WSSession(Session):

    def __init__(self, dispatcher, ssl_enabled, client):
        Session.__init__(self, dispatcher)
        self.ws = client.ws
        self.address = client.address[0] + ":%d" % client.address[1]
        self.name = "WS" if not ssl_enabled else "WSS"
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


class WSApplication(WebSocketApplication):
    def on_open(self, *args, **kwargs):
        session = self.create_session()
        Greenlet.spawn(self.handle_response, session)

    def on_message(self, data, *args, **kwargs):
        if data is None:
            return

        session = self.find_session()
        if session:
            self.handle_data(data, session)

    def on_close(self, *args, **kwargs):
        session = self.find_session()
        if session:
            session.stop()

    def create_session(self):
        client = self.ws.handler.active_client
        return WSSession(self.server.dispatcher, self.server.ssl_enabled, client)

    def find_session(self):
        client = self.ws.handler.active_client
        address = client.address[0] + ":%d" % client.address[1]
        return self.server.dispatcher.get_session_by_address(address)

    def handle_response(self, session):
        try:
            shared = session.dispatcher.shared
            while not (shared.stopped() or shared.paused() or session.stopped()):
                reply = session.response_queue.get()
                session.ws.send(reply)
        except BaseException as e:
            logger.error("error in handling WS session " + str(e) + ' ' + session.address)
        finally:
            session.stop()

    def handle_data(self, data, session):
        try:
            request = json.loads(data)
        except:
            session.send_response({"error": "bad JSON in request"})
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


class WSServer(WebSocketServer):

    def __init__(self, dispatcher, listener, **ssl_args):
        WebSocketServer.__init__(self, listener, Resource({'^/.*': WSApplication}), **ssl_args)
        self.shared = dispatcher.shared
        self.dispatcher = dispatcher.request_dispatcher
        self.host = listener[0]
        self.port = listener[1]

    def start(self):
        WebSocketServer.start(self)
        print_log(("WSS" if self.ssl_enabled else "WS") + " server started on port %d" % self.port)
