import json
import time

from gevent import socket
from gevent.queue import Queue
from gevent.server import StreamServer

from .processor import Session, Dispatcher
from .utils import print_log, logger


class TcpSession(Session):

    def __init__(self, connection, address, dispatcher, ssl_enabled):
        Session.__init__(self, dispatcher)
        self.connection = connection
        self.address = address[0] + ":%d" % address[1]
        self.name = "TCP" if not ssl_enabled else "SSL"
        self.timeout = 1000
        self.response_queue = Queue()
        self.dispatcher.add_session(self)

    def connection(self):
        if self.stopped():
            raise Exception("Session was stopped")
        else:
            return self.connection

    def shutdown(self):
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except:
            # print_log("problem shutting down", self.address)
            pass

        self.connection.close()

    def send_response(self, response):
        try:
            msg = json.dumps(response) + '\n'
        except BaseException as e:
            logger.error('send_response:' + str(e))
        else:
            self.response_queue.put(msg)

    def parse_message(self, message):
        if isinstance(message, basestring):
            self.time = time.time()
            return message.strip()
        else:
            return False


class TcpServer(StreamServer):

    def __init__(self, dispatcher, listener, **ssl_args):
        StreamServer.__init__(self, listener, self.handle, None, 'default', **ssl_args)
        self.shared = dispatcher.shared
        self.dispatcher = dispatcher.request_dispatcher
        self.host = listener[0]
        self.port = listener[1]

    def start(self):
        StreamServer.start(self)
        print_log(("SSL" if self.ssl_enabled else "TCP") + " server started on port %d" % self.port)

    def handle_command(self, raw_command, session):
        try:
            command = json.loads(raw_command)
        except:
            session.send_response({"error": "bad JSON"})
            return

        if 'id' in command and 'method' in command:
            self.dispatcher.push_request(session, command)
            # sleep a bit to prevent a single session from DOSing the queue
            #gevent.sleep(0.01)
        else:
            session.send_response({"error": "syntax error", "request": raw_command})

    def handle(self, connection, address):
        try:
            session = TcpSession(connection, address, self.dispatcher, self.ssl_enabled)
        except BaseException as e:
            logger.error("cannot start TCP session " + str(e) + ' ' + repr(address))
            connection.close()
            return

        try:
            s = connection.makefile()
            while not self.shared.stopped():
                if self.shared.paused():
                    break

                line = s.readline()
                if not line:
                    break

                cmd = session.parse_message(line)
                if not cmd or cmd == 'quit':
                    break
                else:
                    self.handle_command(cmd, session)
                    reply = session.response_queue.get()
                    s.write(reply)
                    s.flush()
        except BaseException as e:
            logger.error("error in handling TCP session " + str(e) + ' ' + repr(address))
        finally:
            session.stop()
