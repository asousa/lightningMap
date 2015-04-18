import ephem
import math
import datetime

class Satellite(object):
  def __init__(self,tle1, tle2, name): 
    self.tle_rec = ephem.readtle(name, tle1, tle2)
    self.curr_time = None
    self.name = name
    self.coords = None    # Long, Lat! XY on a map, but isn't pleasant to say out loud.
  
  def compute(self,plotdate):
    self.tle_rec.compute(plotdate)
    self.curr_time = plotdate
    self.coords = [(180.0/math.pi)*self.tle_rec.sublong, (180.0/math.pi)*self.tle_rec.sublat]

  def coords_at(self,plotdate):
    self.tle_rec.compute(plotdate)
    return self.coords
  
  #def coords(self):
  #  return [(180.0/math.pi)*self.tle_rec.sublong, (180.0/math.pi)*self.tle_rec.sublat]

  #def curr_time(self):
  #  return self.datetime
