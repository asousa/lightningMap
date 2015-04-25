# Load and plot cool logfiles of flyovers:
import os
import time
import datetime as dt
import numpy as np
import csv
from matplotlib import pyplot as plt

sats = ['FB3', 'FB4']

for sat in sats:
  times = []
  counts = []
  peaks = []
  lats = []
  lons = []

  with open('Flyover_Log_'+sat +'.txt','r') as csvfile:
    log = open('Flyover_log_' + sat + 'Filtered.txt','w')
    for row in csv.reader(csvfile, delimiter ='\t'):
      #print row[1]
      #print len(row)
      times.append(dt.datetime.strptime(row[1],'%Y-%m-%dT%H:%M:%S'))
      lats.append(float(row[2]))
      lons.append(float(row[3]))
      counts.append(float(row[4]))
      peaks.append(float(row[5]))


  lats = np.array(lats,'float')
  lons = np.array(lons,'float')
  counts = np.array(counts,'float')
  peaks = np.array(peaks,'float')
  times = np.array(times)


  mask = (lats > 20) & (abs(peaks) > 150)

  print "Hits: " + sat
  for t, la, lo, co, pk in zip(times[mask], lats[mask], lons[mask], counts[mask], peaks[mask]):
    log.write("%s: (%3.3f, %3.3f)\t %d\t%d\r\n" %(t,la,lo,co,pk))
    print "%s: (%3.3f, %3.3f)\t %d\t%d" %(t,la,lo,co,pk)
  fig = plt.figure()
  ax1 = plt.subplot(211)
  ax1.plot(times, abs(peaks),'bo--',label='peak current')
  ax1.set_ylabel('Peak Current (kA)')
  ax4 = ax1.twinx()
  ax4.plot(times, counts,'ro--',label='counts')
  ax4.set_ylabel('Counts')
  #ax1.legend()
  plt.title('All sightings')

  ax2 = plt.subplot(212, sharex = ax1)
  ax2.plot(times[mask], abs(peaks[mask]),'bo--')
  ax2.set_ylabel('Peak Current (kA)')
  #ax2.plot(times[mask], counts[mask],'ro--')
  ax3 = ax2.twinx()
  ax3.plot(times[mask], lats[mask], 'kx--')
  ax3.set_ylabel('Latitude')
  plt.suptitle('Flyovers (' + sat + ')')

plt.show()
