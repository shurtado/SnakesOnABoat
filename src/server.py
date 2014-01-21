""" Run with 'twistd -y server.py """

from twisted.application import service, internet
from twisted.internet import protocol
from twisted.protocols import basic
from twisted.python import log

from game import Game

class Server(basic.LineReceiver):
    """ This server implements the Twisted line receiver server """

    def connectionMade(self):
        """ Checks if we already have that client, if not, adds them to our list """
        self.setRawMode()
        if self not in self.factory.clients:
            self.id = self.transport.getPeer().port
            log.msg("Client", self.id, "connected")
            self.factory.clients.append(self)
            self.factory.game.add_player(self)

    def connectionLost(self, reason):
        """ When a client disconnects, remove them from all lists """
        log.msg("Lost client", self.id)
        self.factory.clients.remove(self)
        self.factory.game.remove_player(self)

    def lineReceived(self, line):
        """ When we receive a line from the client, send it to our game """
        line = line.rstrip()
        if not line:
            return
        log.msg("Received:", repr(line), "from client", self.id)
        response = self.factory.game.send_message(self, line)
        for c in self.factory.clients:
            c.broadcast(response)

    def dataReceived(self, data):
        self.lineReceived(data)

    def broadcast(self, message):
        """ Send a message to the client """
        log.msg("Sending", message, "to client", self.id)
        self.transport.write(message + "\n")

class MyServerFactory(protocol.ServerFactory):
    protocol = Server

    def __init__(self, service):
        self.service = service
        self.clients = []
        self.game = Game(self.service.map, self.service.max_players)

class ServerService(service.Service):
    def __init__(self, map, max_players):
        self.map = map
        self.max_players = max_players

    def startService(self):
        service.Service.startService(self)
        log.msg("Created Game on map", self.map, "with",
                self.max_players, "max players")

"""
application = service.Application("soabserver")
factory = MyServerFactory()
internet.TCPServer(8080, factory).setServiceParent(application)"""
