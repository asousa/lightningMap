#import threading
import time
from Queue import Queue
import logging
import numpy as np
import os
import datetime
#import matplotlib
#matplotlib.use('GTKAgg')
#from matplotlib import pyplot as plt
#from mpl_toolkits.basemap import Basemap
import datetime
import ephem
import math
#from StreamReader import StreamReader
import json
from GLD_file_tools import GLD_file_tools
from check_flyover import check_flyover
from satellite import Satellite

# Websocket stuff
# from autobahn.twisted.websocket import WebSocketServerProtocol, \
#     WebSocketServerFactory
# import sys
# from twisted.python import log
# from twisted.internet import reactor

# import GLD_server_instance


class GLD_server_instance(object):
  def __init__(self):
    # -------------------------------
    # Parameters!
    # -------------------------------
    self.GLD_root  = 'alex/array/home/Vaisala/feed_data/GLD';
    self.NLDN_root = 'alex/array/home/Vaisala/feed_data/NLDN';
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

    self.G = GLD_file_tools(self.GLD_root, prefix='GLD')
    self.N = GLD_file_tools(self.NLDN_root,prefix='NLDN')
    #self.time_in = datetime.datetime(2015,3,26,12,00,00)

    self.do_GLD = True
    self.do_NLDN = True
    self.do_sats = True

    # Satellite initialization
    #sat = Firebird(FB4_line1, FB4_line2, "Firebird 4")
    if (self.do_sats):
      self.Firebird_4 = Satellite(self.FB4_line1, self.FB4_line2, "Firebird 4")
      self.Firebird_3 = Satellite(self.FB3_line1, self.FB3_line2, "Firebird 3")

    self.plottime = None

  def interpret(self,message):
    ''' Received a message! What do?? '''
    print message
    # if (message == 'refresh GLD'):
    #   self.G = GLD_file_tools(self.GLD_root, prefix='GLD')
    # else:  
    rec_time = datetime.datetime.strptime(message, "%Y-%m-%dT%H:%M:%S") 
    self.plottime = rec_time   # Set time to compute at
    return self.build_json_at(rec_time)

  def build_json_at(self,time_in):

    geo_json = []

    # ------ Satellites --------
    if self.do_sats:
      self.Firebird_4.compute(self.plottime)
      self.Firebird_3.compute(self.plottime)
          # Create record for satellites
      #curr_sat_pos = sat.coords_at(plotdate)

      for sat in [self.Firebird_3, self.Firebird_4]:
        geo_json.extend( [ {"type": "Feature",
                    "name": "Satellite",
                    "satname": sat.name,
                        "geometry": {
                            "type": "Point",
                            "coordinates": sat.coords,
                            }, "time":self.plottime.isoformat()
                          } ] )




    # ----- GLD ----------------
    if self.do_GLD:
      new_flashes, new_times = self.G.load_flashes(time_in, self.window_delta)

      if new_flashes is not None:

        if self.do_sats:
          bb_fb4 = check_flyover(self.Firebird_4, new_flashes, new_times)
          bb_fb3 = check_flyover(self.Firebird_3, new_flashes, new_times)
          geo_json.extend(bb_fb4)
          geo_json.extend(bb_fb3)


        radii = np.round(np.log2(abs(new_flashes[:,self.mag_ind])))

        # Create record for flashes
        gld_json = [ {"type": "Feature",
                      "name": "GLD",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [lon,lat],
                            }, "radius": radius,
                               "kA": kA,
                               "time": dt.isoformat()}
                        for lon,lat,radius,kA,dt in zip(new_flashes[:,self.lon_ind],
                                                        new_flashes[:,self.lat_ind], 
                                                        radii, new_flashes[:,self.mag_ind], new_times) ]
        geo_json.extend(gld_json)
      


    # -------- NLDN ----------
    if self.do_NLDN:
      new_flashes, new_times = self.N.load_flashes(time_in, self.window_delta)
      if new_flashes is not None:
        radii = np.round(np.log2(abs(new_flashes[:,self.mag_ind])))
            # Create record for flashes
        nldn_json = [ {"type": "Feature",
                      "name": "NLDN",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [lon,lat],
                            }, "radius": radius,
                               "kA": kA,
                               "time": dt.isoformat()}
                        for lon,lat,radius,kA,dt in zip(new_flashes[:,self.lon_ind],
                                                        new_flashes[:,self.lat_ind], 
                                                        radii, new_flashes[:,self.mag_ind], new_times) ]
        geo_json.extend(nldn_json) 





    
    return json.dumps(geo_json, ensure_ascii = False).encode('utf8')  

