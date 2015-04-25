# Check for flyovers:
import numpy as np
import datetime
import math
import logging

def check_flyover(satellite, flashes, flashtimes=None, logfile=None, JSON=True,
                  lat_lim = [-200,200], lon_lim = [-100,100], td=datetime.timedelta(0,0,0,0,1,0)):
  '''Satellite: Firebird object.
     flashes: ndarray of flash entries (GLD format)
  '''

  lat_ind = 7;
  lon_ind = 8;
  mag_ind = 9;

  s = satellite.coords
  t = satellite.curr_time
  
  #print "Sat Coords:", s

  R_earth = 6378; # km
  deg_to_km = R_earth*math.pi/180; # ~ 110 km per degree
  km_to_deg = 1.0/deg_to_km;

  # lat_bounds = km_to_deg*np.array([-200, 200]) + s[1];
  # lon_bounds = km_to_deg*np.array([-100, 100]) + s[0];
  lat_bounds = km_to_deg*np.array(lat_lim) + s[1];
  lon_bounds = km_to_deg*np.array(lon_lim) + s[0];
  #print "Lat bounds: ", lat_bounds
  #print "Lon bounds: ", lon_bounds
  if flashtimes is not None:
    delay = t - flashtimes
    flyovers = flashes[#(delay < td) &
                   (flashes[:,lat_ind] > lat_bounds[0]) &
                   (flashes[:,lat_ind] < lat_bounds[1]) & 
                   (flashes[:,lon_ind] > lon_bounds[0]) &
                   (flashes[:,lon_ind] < lon_bounds[1]) ];




  logging.info('Total Flyovers : ' + str(flyovers.shape[0]))


  total_counts = flyovers.shape[0]
  if total_counts > 0:
    #print flyovers
    peak_current = flyovers[np.argmax(abs(flyovers[:,mag_ind])),mag_ind]
  else:
    peak_current = 0


  if logfile is not None:
    if (total_counts > 0):
      logfile.write('%s\t%s\t%3.3f\t%3.3f\t%d\t%d\r\n' %
        (satellite.name, t.isoformat(), s[1], s[0], total_counts, peak_current))  
#Create a geoJSON polygon for the region
  if JSON:
    bounding_box = [{
      "type": "Feature",
      "name": "Box",
      "properties": {"satname": satellite.name, "counts": total_counts},
      "geometry": {
          "type": "Polygon",
          "coordinates": [[
                          [lon_bounds[0],lat_bounds[0]],
                          [lon_bounds[0],lat_bounds[1]],
                          [lon_bounds[1],lat_bounds[1]],
                          [lon_bounds[1],lat_bounds[0]]

                        ]]
      }}]
  else:
    bounding_box = None

  return bounding_box, total_counts, peak_current