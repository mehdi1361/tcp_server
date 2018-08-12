from twisted.internet import reactor, protocol


class EchoClient(protocol.Protocol):
    def connectionMade(self):
        self.transport.write("""{"username": "mehdi", "password":"Mehdi#1361", "troops_id": [19, 14, 10, 22]}""")

    def dataReceived(self, data):
        print "Server said:", data
        # self.transport.loseConnection()

class EchoFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):

        return EchoClient()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed."
        # reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost."
        # reactor.stop()


# lst_client = [EchoFactory(), EchoFactory()]
# for client in lst_client:
reactor.connectTCP("127.0.0.1", 9092, EchoFactory())
reactor.run()
