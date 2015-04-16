import threading
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
#import datetime
#import ephem
#import math
class StreamReader(object):
    """ Threaded StreamReader object. On initialization, starts 
    a background thread to watch for new additions to the GLD logfile.
    """
 
    def __init__(self, filename, interval=1, skip_to_end=True):
        """ Constructor

        :type interval: int
        :param interval: Check interval, in seconds
        """
        logging.debug("Initializing stream reader...")
        self.interval = interval
        self.curr_file = filename
        self.q = Queue()
        self.skip_to_end = skip_to_end
        thread = threading.Thread(target=self.run, args=(),name='Stream Watcher')
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
 
    def run(self):
        """ Method that runs forever """
        thefile = open(self.curr_file,'rb')
        linebuff = []
        if self.skip_to_end:
          if thefile.tell()== 0:
            logging.debug('seeking to end of file')
            thefile.seek(0,2)
        while True:
          # Do something
          #print('checking for freshness')
          line = thefile.readline()
          
          # Did we read anything?
          if line:
            #logging.debug(line)
            #self.q.put(line)
            vec = line.split('\t')
            if vec[-1]== u'1\r\n':  # Full line
              tmp = linebuff[0:-1] + vec # Still don't know why it adds an extra '' in there :x
              linebuff = []
              #print len(tmp)
              #logging.debug(len(tmp))
            
              if len(tmp)==25: 
           
                self.q.put(np.array(tmp[1:11]),'float')
                #self.q.put([int(tmp[1]),int(tmp[2]),int(tmp[3]),int(tmp[4]),int(tmp[5]),
                #              int(tmp[6]),int(tmp[7]),float(tmp[8]),float(tmp[9]),int(tmp[10])])
                              
                #logging.debug(([int(tmp[1]),int(tmp[2]),int(tmp[3]),int(tmp[4]),int(tmp[5]),
                #              int(tmp[6]),int(tmp[7]),float(tmp[8]),float(tmp[9]),int(tmp[10])]))
              else:
                logging.debug("Row size mismatch ! size = %i" % len(tmp) )
            else:                   # Half line
              linebuff = vec

          #logging.debug("Q size: %i " % self.q.qsize())
          time.sleep(self.interval)
 
    def get(self):
      return self.q.get()
      
    def get_all(self):
      lines = []
      qlen = self.q.qsize();
      # logging.debug('Popping %i lines' % qlen)
      
      if qlen == 0:
        return
      else:
        while qlen > 0:
          qlen -= 1
          try:
            row = self.q.get()
            lines.append(np.asarray(row,'float'))
          except ValueError,e:
            logging.debug('error',e,'row is: ',row)
            
        logging.debug('Popped %i lines' % len(lines))
        return np.asarray(lines,'float')