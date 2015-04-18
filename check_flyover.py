# Check for flyovers:
import numpy as np
import datetime
import math

def check_flyover(satellite, flashes, flashtimes=None,
                       td=datetime.timedelta(0,0,0,0,1,0), logfile = 'flyover_log.txt'):
  '''Satellite: Firebird object. If checktime is provided, will update ephemeris.
     flashes: ndarray of flash entries (GLD format)
  '''

  lat_ind = 7;
  lon_ind = 8;
  mag_ind = 9;

  s = satellite.coords
  t = satellite.curr_time
  
  print "Sat Coords:", s

  R_earth = 6378; # km
  deg_to_km = R_earth*math.pi/180; # ~ 110 km per degree
  km_to_deg = 1.0/deg_to_km;

  lat_bounds = km_to_deg*np.array([-200, 200]) + s[1];
  lon_bounds = km_to_deg*np.array([-100, 100]) + s[0];

  print "Lat bounds: ", lat_bounds
  print "Lon bounds: ", lon_bounds
  if flashtimes is not None:
    delay = t - flashtimes
    flyovers = flashes[#(delay < td) &
                   (flashes[:,lat_ind] > lat_bounds[0]) &
                   (flashes[:,lat_ind] < lat_bounds[1]) & 
                   (flashes[:,lon_ind] > lon_bounds[0]) &
                   (flashes[:,lon_ind] < lon_bounds[1]) ];


  print 'Total Flyovers : ', flyovers.shape[0]

  total_counts = flyovers.shape[0]
# Create a geoJSON polygon for the region
  bounding_box = [{
    "type": "Feature",
    "name": "box",
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

  return bounding_box