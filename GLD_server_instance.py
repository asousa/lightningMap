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

class GLD_server_instance(object):
  def __init__(self):
    # -------------------------------
    # Parameters!
    # -------------------------------
    self.GLD_root  = 'alex/array/home/Vaisala/feed_data/GLD';
    self.NLDN_root = 'alex/array/home/Vaisala/feed_data/NLDN';
    #tail_len = 20000;
    self.window_delta = datetime.timedelta(minutes=1);
    self.lat_lim = [-200, 200]
    self.lon_lim = [-100, 100]
    
    # list of Satellite objects
    self.sats = []

    # Firebird TLEs
    # self.FB4_line1 = "1 40378U 15003C   15100.58013485  .00011386  00000-0  58112-3 0  9991";
    # self.FB4_line2 = "2 40378  99.1244 121.5989 0163653 114.5990 247.2373 15.05957022 10376";

    # self.FB3_line1 = "1 40377U 15003B   15107.62395886  .00014462  00000-0  73378-3 0  9999";
    # self.FB3_line2 = "2 40377 099.1226 129.9288 0163094 091.7149 270.2788 15.06141595 11435";

    # Retrieved 10.20.2015
    self.FB4_line1 = "1 40378U 15003C   15293.75287141  .00010129  00000-0  48835-3 0  9990";
    self.FB4_line2 = "2 40378  99.1043 350.5299 0153633 201.4233 158.0516 15.09095095 39471";

    self.FB3_line1 = "1 40377U 15003B   15293.75560501  .00010189  00000-0  49167-3 0  9998";
    self.FB3_line2 = "2 40377  99.1045 350.5247 0153380 201.4540 158.0211 15.09095594 39471";

    self.lat_ind = 7;
    self.lon_ind = 8;
    self.mag_ind = 9;

    self.G = GLD_file_tools(self.GLD_root, prefix='GLD')
    self.N = GLD_file_tools(self.NLDN_root,prefix='NLDN')
    #self.time_in = datetime.datetime(2015,3,26,12,00,00)

    self.do_GLD = True
    self.do_NLDN = True
    self.do_sats = True
    self.return_JSON = True



    # Satellite initialization
    #sat = Firebird(FB4_line1, FB4_line2, "Firebird 4")
    if (self.do_sats):
      # self.Firebird_4 = Satellite(self.FB4_line1, self.FB4_line2, "Firebird 4")
      # self.Firebird_3 = Satellite(self.FB3_line1, self.FB3_line2, "Firebird 3")
      self.sats.append(Satellite(self.FB4_line1, self.FB4_line2, "Firebird 4"))
      self.sats.append(Satellite(self.FB3_line1, self.FB3_line2, "Firebird 3"))


    self.plottime = None

  def interpret(self,message):
    ''' Received a message! What do?? '''
    msg_obj = json.loads(message)

    if 'enables' in msg_obj:
      self.do_GLD = msg_obj["enables"]["GLD"]
      self.do_NLDN =msg_obj["enables"]["NLDN"]
      self.do_sats =msg_obj["enables"]["Sats"]

    if 'persist' in msg_obj:
      self.window_delta = datetime.timedelta(seconds = int(msg_obj["persist"]))

    if 'time' in msg_obj:
      rec_time = datetime.datetime.strptime(msg_obj["time"], "%Y-%m-%dT%H:%M:%S") 
      print "Request time: ", rec_time
      self.plottime = rec_time   # Set time to compute at
      return self.build_json_at(rec_time)

#      self.window_delta = datetime.timedelta(seconds=int(lines[1]))

  def build_json_at(self,time_in):
    geo_json = []

    # ------ Satellites --------
    #if self.do_sats:
    for sat in self.sats:
      sat.compute(self.plottime)
      # self.Firebird_4.compute(self.plottime)
      # self.Firebird_3.compute(self.plottime)
   
    if self.return_JSON:
      for sat in self.sats: #[self.Firebird_3, self.Firebird_4]:
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

        # if self.do_sats:

        #   bb_fb4,_,_ = check_flyover(self.Firebird_4, new_flashes, new_times, td = self.window_delta,
        #           lat_lim = self.lat_lim, lon_lim = self.lon_lim, JSON = self.return_JSON)
        #   bb_fb3,_,_ = check_flyover(self.Firebird_3, new_flashes, new_times, td = self.window_delta,
        #           lat_lim = self.lat_lim, lon_lim = self.lon_lim,  JSON =self.return_JSON)

        #   if self.return_JSON:
        #     geo_json.extend(bb_fb4)
        #     geo_json.extend(bb_fb3)
        # bb = []
        for sat in self.sats:
          bb_tmp,_,_ = check_flyover(sat, new_flashes, new_times, td = self.window_delta,
                    lat_lim = self.lat_lim, lon_lim = self.lon_lim, JSON = self.return_JSON)
          
          #bb.extend(bb_tmp)

          if self.return_JSON:
            geo_json.extend(bb_tmp)
          
        if self.return_JSON:



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
        if self.return_JSON:
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





    if self.return_JSON:
      return json.dumps(geo_json, ensure_ascii = False).encode('utf8')  



  def log_sightings(self, fb3_file=None, fb4_file=None, JSON=False):

    new_flashes, new_times = self.G.load_flashes(self.plottime, self.window_delta)

    if new_flashes is not None:
      for sat in self.sats:
        sat.compute(self.plottime)

      if fb3_file is not None:
        #self.Firebird_3.compute(self.plottime)
        check_flyover(self.Firebird_3, new_flashes, new_times, td = self.window_delta,
                  lat_lim = self.lat_lim, lon_lim = self.lon_lim, logfile=fb3_file)

      if fb4_file is not None:
        #self.Firebird_4.compute(self.plottime)
        check_flyover(self.Firebird_4, new_flashes, new_times, td = self.window_delta,
                  lat_lim = self.lat_lim, lon_lim = self.lon_lim, logfile=fb4_file)
    
