#import threading
import time
from Queue import Queue
import logging
import numpy as np
import os
import datetime
import ephem
import math

import json
from GLD_file_tools import GLD_file_tools
from check_flyover import check_flyover
from satellite import Satellite

# Websocket stuff
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
import sys
from twisted.python import log
from twisted.internet import reactor

from GLD_server_instance import GLD_server_instance

# -------------------------------
# Websocket Object
# -------------------------------

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.sendMessage('Bronichiwa', False)

    def onOpen(self):
        print("Initializing the thing")
        self.D = GLD_server_instance()
        print("WebSocket connection open.")


    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        # self.sendMessage(payload, isBinary)
        # Decode message:
        self.sendMessage(self.D.interpret(payload),False)
    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

#   # -------------------------------
#   # Main Program
#   # -------------------------------

  # Logger
  logging.basicConfig(level=logging.DEBUG,
                      format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                      )

  factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
  factory.protocol = MyServerProtocol
  # factory.setProtocolOptions(maxConnections=2)

  # Start them shits
  reactor.listenTCP(9000, factory)
  reactor.run()
