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
import fnmatch



GLD_root = 'alex/array/home/Vaisala/feed_data/GLD';

# ----------------------------------------------------------
# A set of modules to quickly search and parse GLD entries
# ----------------------------------------------------------

def get_file_at(t):
  ''' (Where t is a datetime object)
      Returns a tuple <datetime, filepath>
      Probably has issues loading times near midnight, etc
  '''
  matches = []
  #for root, dirnames, filenames in os.walk(GLD_root):
  #filepaths = []
  #startdates = []
  file_list = []
  # Get datetime objects for each file in directory:
  for root, dirs, files in os.walk(GLD_root):
    for file in files:
      if file.endswith(".dat"):
        print file
        file_list.append([(datetime.datetime.strptime(file,'GLD-%Y%m%d%H%M%S.dat')),
                          (os.path.join(root,file))])
        #filepaths.append(os.path.join(root,file))
        #startdates.append(datetime.datetime.strptime(file,'GLD-%Y%m%d%H%M%S.dat'))
  
  file_list.sort(key=lambda tup: tup[0])
  #print file_list
  
  startfile = filter(lambda row: row[0] <= t, file_list)[-1]
  print startfile
  return startfile

def load_flashes(filepath,t, dt = datetime.timedelta(0,0,0,0,1,0)):
  '''filepath: GLD file to sift thru
     t: datetime object to search around
     dt: datetime.timedelta 
  '''
  
  tprev = t - datetime.timedelta(0,0,0,0,1,0)
  print t
  print tprev
  #buff_size = 100000 # bytes
  # Binary search thru entries:
  imax = np.floor(os.path.getsize(filepath)/2).astype('int')
  imin = 0
  thefile = open(filepath,'r')
  
  # Find closest index to target time:
  t_ind = recursive_search_kernel(thefile, t, imin, imax)
  print datetime_from_row(parse_line(thefile,t_ind))
  
  # Find closest index to window time:
  tprev_ind = recursive_search_kernel(thefile,tprev,imin,imax)
  print datetime_from_row(parse_line(thefile,tprev_ind))
  
  # Load rows between tprev_ind and t_ind:
  rows = []
  while (thefile.tell() < t_ind):
    rows.append(parse_line(thefile,thefile.tell()))
  print " Found " + str(len(rows)) + " entries between " + str(tprev) + " and " + str(t)
     

     
def recursive_search_kernel(thefile, target_time, imin, imax ):
  ''' Recursively searches thefile (previously open) for the closest entry
      to target_time (datetime object)
  '''
  imid = imin + ((imax - imin)/2)
  l = parse_line(thefile,imid)
  #print l
  y,m,d,H,M,S = l[0:6].astype('int')
  curr_time = datetime.datetime(y,m,d,H,M,S)
  
  if abs(imin - imax) <= 1:
    return imin
  else:
    if curr_time > target_time:
      imax = imid
    else:
      imin = imid
    # Uncomment this to show recursion (hella sweet)  
    #print imin, imax, imax-imin, curr_time
    return recursive_search_kernel(thefile,target_time,imin,imax)
    
def parse_line(thefile, theindex):
  '''
  Returns a parsed line; recursively skips forward if line isn't full-length
  '''
  thefile.seek(theindex,0)
  line = thefile.readline()
  vec = line.split('\t')
  if len(vec)==25: 
    return np.array(vec[1:11],'float')
  else:
    return parse_line(thefile,thefile.tell())

def datetime_from_row(row):
  y,m,d,H,M,S = row[0:6].astype('int')
  return datetime.datetime(y,m,d,H,M,S)




# ---------------------------
# Main block
# ---------------------------  
t = datetime.datetime(2015,03,26,12,01,00)
#startfile, startfile_time = get_file_at(t)
startfile ='alex/array/home/Vaisala/feed_data/GLD/2015-03-26/GLD-201503260223.dat'
load_flashes(startfile,t)