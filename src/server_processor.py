import sys
import time
import gevent
from gevent import Greenlet
from gevent.queue import Queue, Empty

from .processor import Processor
from .utils import Hash, print_log, logger
from .version import VERSION
from .ircthread import IrcThread


class ServerProcessor(Processor):

    def __init__(self, config, shared):
        Processor.__init__(self)
        self.config = config
        self.shared = shared
        self.irc_queue = Queue()
        self.peers = {}

        if self.config.get('server', 'irc') == 'yes':
            self.irc = IrcThread(self, self.config, self.irc_queue)
            self.irc.start()
            Greenlet.spawn(self.read_irc_results)
        else:
            self.irc = None

    def read_irc_results(self):
        while True:
            try:
                event, params = self.irc_queue.get(timeout=1)
            except Empty:
                continue
            #logger.info(event + ' ' + repr(params))
            if event == 'join':
                nick, ip, host, ports = params
                self.peers[nick] = (ip, host, ports)
            if event == 'quit':
                nick = params[0]
                if self.peers.get(nick):
                    self.peers.pop(nick)

    def get_peers(self):
        return self.peers.values()

    def process(self, request):
        method = request['method']
        params = request['params']
        result = None

        if method == 'server.banner':
            result = self.config.get('server', 'banner').replace('\\n', '\n')

        elif method == 'server.donation_address':
            result = self.config.get('server', 'donation_address')

        elif method == 'server.peers.subscribe':
            result = self.get_peers()

        elif method == 'server.version':
            result = VERSION

        else:
            raise BaseException("unknown method: %s" % repr(method))

        return result
