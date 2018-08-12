from twisted.internet import reactor, protocol

class EchoClient(protocol.Protocol):
    def __init__(self, message):
        self.message = message

    def connectionMade(self):
        self.transport.write(self.message)

    def dataReceived(self, data):
        print "Server said:", data
        # self.transport.loseConnection()

class EchoFactory(protocol.ClientFactory):
    def __init__(self, message):
        self.message = message

    def buildProtocol(self, addr):

        return EchoClient(self.message)

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed."
        # reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost."


class client:
    def __init__(self, user):
        self.user = user
        self.login_msg = str({"username": user,
                              "password": "Mehdi#1361",
                              "troops_id": [19, 14, 10, 22]
                              }
                             )
        self.channel = EchoFactory(self.login_msg)
        self.reactor = reactor

    def run(self):
        reactor.connectTCP("127.0.0.1", 9092, self.channel)
        reactor.run()