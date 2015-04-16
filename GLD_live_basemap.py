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
# -------------------------------
# Parameters!
# -------------------------------
GLD_root = 'alex/array/home/Vaisala/feed_data/GLD';

#tail_len = 20000;
window_delta = datetime.timedelta(0,0,0,0,1,0); # y,m,d,H,M,S
hold_time = 60
FB4_line1 = "1 40378U 15003C   15100.58013485  .00011386  00000-0  58112-3 0  9991";
FB4_line2 = "2 40378  99.1244 121.5989 0163653 114.5990 247.2373 15.05957022 10376";


#lat_ind = 7;
#lon_ind = 8;
firstread = True

# -------------------------------
# Wrapper module for satellite location
# -------------------------------
class Firebird(object):
  def __init__(self,tle1, tle2, name): 
    self.tle_rec = ephem.readtle(name, tle1, tle2)
  
  def compute(self,plotdate):
    self.tle_rec.compute(plotdate)
    
  def coords_at(self,plotdate):
    self.tle_rec.compute(plotdate)
    return [(180.0/math.pi)*self.tle_rec.sublong, (180.0/math.pi)*self.tle_rec.sublat]
     
# -------------------------------
# Get most-current file!
# -------------------------------
def get_newest_file():
  directories = sorted([ f for f in os.listdir(GLD_root)])
  # Get most-recent directory:
  curr_GLD_folder = GLD_root +'/' + directories[-1]
  print "Most recent directory = %s" % curr_GLD_folder
  # Get most-recent file:
  files = sorted([f for f in os.listdir(curr_GLD_folder)])
  print files
  return curr_GLD_folder + '/' + files[-1]
      
# ------------------------------
# Update the map!
# ------------------------------    
def update_map(flashes,fig,ax,background, plotdate, satellite=None):
  #print flashes[:,8], flashes[:,7]
  fig.canvas.restore_region(background)
  #background = fig.canvas.copy_from_bbox(ax.bbox)
  x,y = map(flashes[:,8],flashes[:,7])
  mag = np.log2(abs(flashes[:,9]))
  points = map.plot(x,y,'ro',markeredgecolor=[1,0,0], markersize=2)[0]  
  #for lon, lat, mag in zip(flashes[:,8],flashes[:,7],flashes[:,9]):
  #  x,y = map(lon, lat)
  #  print x, y
  #  msize = np.log2(abs(mag))        
  #  point = ax.plot(x,y,'o',markerfacecolor=[1,0,0],markeredgecolor=[1,0,0],markersize=msize);

  print plotdate
  #CS=map.nightshade(plotdate,alpha=0.25)
  
  if satellite is not None:
    lon, lat = sat.coords_at(plotdate)
    fbx, fby = map(lon, lat)
    print "Firebird Location: ", lon, lat
    fb = map.plot(fbx, fby,'*',markerfacecolor=[1,0.8,0],markersize=24)[0];
  

  ax.draw_artist(points)
  ax.draw_artist(fb)
  #ax.draw_artist(CS)
  ax.set_title('GLD flashes, %s (UTC)\nHold Time = %s mins' % (plotdate, window_delta.seconds/60))
  fig.canvas.set_window_title(str(plotdate))
  # fill in the axes rectangle
  fig.canvas.blit(ax.bbox)
  fig.canvas.draw()
  #plt.draw()

# ------------------------------
# Update the map! (plotting fresh each time)
# ------------------------------ 
def update_fresh(flashes,fig,ax, plotdate, satellite=None):
  fig.clf()
  map = Basemap(projection='mill',lon_0=0)
  map.drawcoastlines()
  map.drawparallels(np.arange(-90,90,30),labels=[1,0,0,0])
  map.drawmeridians(np.arange(map.lonmin,map.lonmax+30,60),labels=[0,0,0,1])
  map.drawmapboundary(fill_color='b')
  map.fillcontinents(color='white',lake_color='b')
  
  x,y = map(flashes[:,8],flashes[:,7])
  mag = np.log2(abs(flashes[:,9]))
  points = map.plot(x,y,'ro',markeredgecolor=[1,0,0], markersize=2)[0]  
  #for lon, lat, mag in zip(flashes[:,8],flashes[:,7],flashes[:,9]):
  #  x,y = map(lon, lat)
  #  print x, y
  #  msize = np.log2(abs(mag))        
  #  point = ax.plot(x,y,'o',markerfacecolor=[1,0,0],markeredgecolor=[1,0,0],markersize=msize);

  print plotdate
  CS=map.nightshade(plotdate,alpha=0.25)
  
  if satellite is not None:
    lon, lat = sat.coords_at(plotdate)
    fbx, fby = map(lon, lat)
    print "Firebird Location: ", lon, lat
    fb = map.plot(fbx, fby,'*',markerfacecolor=[1,0.8,0],markersize=24)[0];
  

  plt.title('GLD flashes, %s (UTC)\nHold Time = %s mins' % (plotdate, window_delta.seconds/60))
  fig.canvas.set_window_title(str(plotdate))
  #fig.canvas.draw()  
  plt.draw()
# -------------------------------
# Main Program
# -------------------------------

# Logger
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

# Data feed
feed = StreamReader(get_newest_file(), interval=0, skip_to_end=True)
#feed = StreamReader("herpderp.txt",interval=0, skip_to_end=False)

# Satellite initialization
sat = Firebird(FB4_line1, FB4_line2, "Firebird 4")

# Plot initialization
fig, ax = plt.subplots(1,1,figsize=(16,10))
#ax.set_xlim(-180,180)
#ax.set_ylim(-90,90)
fig.canvas.set_window_title(str(datetime.datetime.utcnow()))
map = Basemap(projection='mill',lon_0=0)
map.drawcoastlines()
map.drawparallels(np.arange(-90,90,30),labels=[1,0,0,0])
map.drawmeridians(np.arange(map.lonmin,map.lonmax+30,60),labels=[0,0,0,1])
map.drawmapboundary(fill_color='b')
map.fillcontinents(color='white',lake_color='b')

ax.hold(True)

plt.show(False)
plt.draw()

background = fig.canvas.copy_from_bbox(ax.bbox)
flash_list = None
time_list = None
while(1):
  time.sleep(1)
  #print "still here"
  new_flashes = feed.get_all()

  if new_flashes is not None:
    if flash_list is None:
      flash_list = new_flashes
      time_list = np.array([datetime.datetime(y,m,d,H,M,S) for y,m,d,H,M,S in new_flashes[:,0:6].astype('int')])
    else:
      flash_list = np.concatenate((flash_list, new_flashes))
      time_list = np.concatenate((time_list, np.array([datetime.datetime(y,m,d,H,M,S) for y,m,d,H,M,S in new_flashes[:,0:6].astype('int')]) ))
      print time_list.shape
    plotdate = time_list[-1]
    # remove out-of-date entries
    print flash_list.shape
    flash_list = flash_list[plotdate - time_list < window_delta,:]
    time_list = time_list[plotdate - time_list < window_delta]
    print flash_list.shape
    
    #update_map(flash_list,fig,ax,background,plotdate,satellite=sat)
    update_fresh(flash_list,fig,ax,plotdate,satellite=sat)
