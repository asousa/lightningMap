import threading
import time
from Queue import Queue
import logging
import numpy as np
import os
import datetime
import matplotlib
matplotlib.use('GTKAgg')
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
import datetime
import ephem
import math
from StreamReader import StreamReader
import json
from GLD_file_tools import GLD_file_tools
from check_flyover import check_flyover
from satellite import Satellite

from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
import sys

from twisted.python import log
from twisted.internet import reactor
# -------------------------------
# Websocket Object
# -------------------------------

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.sendMessage('Bronichiwa', False)

    def onOpen(self):
        print("Initializing the thing")
        self.D = Dataset()
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



# Data feed
#feed = StreamReader(get_newest_file(), interval=0, skip_to_end=True)
#feed = StreamReader("herpderp.txt",interval=0, skip_to_end=False)

class Dataset(object):
  def __init__(self):
    # -------------------------------
    # Parameters!
    # -------------------------------
    self.GLD_root = 'alex/array/home/Vaisala/feed_data/GLD';

    #tail_len = 20000;
    self.window_delta = datetime.timedelta(0,0,0,0,1,0); # y,m,d,H,M,S
    
    # Firebird TLEs
    self.FB4_line1 = "1 40378U 15003C   15100.58013485  .00011386  00000-0  58112-3 0  9991";
    self.FB4_line2 = "2 40378  99.1244 121.5989 0163653 114.5990 247.2373 15.05957022 10376";

    self.FB3_line1 = "1 40377U 15003B   15107.62395886  .00014462  00000-0  73378-3 0  9999";
    self.FB3_line2 = "2 40377 099.1226 129.9288 0163094 091.7149 270.2788 15.06141595 11435";

    self.lat_ind = 7;
    self.lon_ind = 8;
    self.mag_ind = 9;

    self.G = GLD_file_tools(self.GLD_root)

    #self.time_in = datetime.datetime(2015,3,26,12,00,00)

    # Satellite initialization
    #sat = Firebird(FB4_line1, FB4_line2, "Firebird 4")
    self.Firebird_4 = Satellite(self.FB4_line1, self.FB4_line2, "Firebird 4")
    self.Firebird_3 = Satellite(self.FB3_line1, self.FB3_line2, "Firebird 3")


  def interpret(self,message):
    ''' Received a message! What do?? '''
    #rec_time = datetime.datetime.strptime(message, "%Y-%m-%dT%H:%M:%S")  
    rec_time = datetime.datetime.strptime(message, "%Y/%m/%d %H:%M:%S")  

    return self.build_json_at(rec_time)

  def build_json_at(self,time_in):

    new_flashes, new_times = self.G.load_flashes(time_in, self.window_delta)

    self.Firebird_4.compute(new_times[-1])
    self.Firebird_3.compute(new_times[-1])

    bb_fb4 = check_flyover(self.Firebird_4, new_flashes, new_times)
    bb_fb3 = check_flyover(self.Firebird_3, new_flashes, new_times)

    print bb_fb4
    print bb_fb3
    if new_flashes is not None:
      
      plotdate = new_times[-1]
      radii = np.round(np.log2(abs(new_flashes[:,self.mag_ind])))

      # Create record for flashes
      geo_json = [ {"type": "Feature",
                    "name": "Flash",
                      "geometry": {
                          "type": "Point",
                          "coordinates": [lon,lat],
                          }, "radius": radius,
                             "kA": kA,
                             "time": dt.isoformat()}
                      for lon,lat,radius,kA,dt in zip(new_flashes[:,self.lon_ind],
                                                      new_flashes[:,self.lat_ind], 
                                                      radii, new_flashes[:,self.mag_ind], new_times) ]

      # Create record for satellite
      #curr_sat_pos = sat.coords_at(plotdate)
      for sat in [self.Firebird_3, self.Firebird_4]:
        sat_json = [ {"type": "Feature",
                    "name": "Satellite",
                    "satname": sat.name,
                        "geometry": {
                            "type": "Point",
                            "coordinates": sat.coords,
                            }, "time":plotdate.isoformat()
                            } ]
        geo_json.extend(sat_json)
        geo_json.extend(bb_fb4)
        geo_json.extend(bb_fb3)


      return json.dumps(geo_json, ensure_ascii = False).encode('utf8')  



if __name__ == '__main__':
#   # -------------------------------
#   # Parameters!
#   # -------------------------------
#   GLD_root = 'alex/array/home/Vaisala/feed_data/GLD';

#   #tail_len = 20000;
#   window_delta = datetime.timedelta(0,0,0,0,1,0); # y,m,d,H,M,S
#   hold_time = 60

#   # Firebird TLEs
#   FB4_line1 = "1 40378U 15003C   15100.58013485  .00011386  00000-0  58112-3 0  9991";
#   FB4_line2 = "2 40378  99.1244 121.5989 0163653 114.5990 247.2373 15.05957022 10376";

#   FB3_line1 = "1 40377U 15003B   15107.62395886  .00014462  00000-0  73378-3 0  9999";
#   FB3_line2 = "2 40377 099.1226 129.9288 0163094 091.7149 270.2788 15.06141595 11435";

#   lat_ind = 7;
#   lon_ind = 8;
#   mag_ind = 9;

#   # -------------------------------
#   # Main Program
#   # -------------------------------

  # Logger
  logging.basicConfig(level=logging.DEBUG,
                      format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                      )






#   G = GLD_file_tools(GLD_root)


#   time_in = datetime.datetime(2015,3,26,12,00,00)



#   # Satellite initialization
#   #sat = Firebird(FB4_line1, FB4_line2, "Firebird 4")
#   Firebird_4 = Satellite(FB4_line1, FB4_line2, "Firebird 4")
#   Firebird_3 = Satellite(FB3_line1, FB3_line2, "Firebird 3")

#   #build_json_at(time_in,G,Firebird_3, Firebird_4)
  
# # Dump to json file:
# #with open("flashes_static.json","w") as outfile:
# #  json.dump(geo_json,outfile,indent=4)

  #log.startLogging(sys.stdout)

  factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
  factory.protocol = MyServerProtocol
  # factory.setProtocolOptions(maxConnections=2)

  # Start them shits
  reactor.listenTCP(9000, factory)
  reactor.run()