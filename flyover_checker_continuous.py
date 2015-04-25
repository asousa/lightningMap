import os
import time
import datetime as dt
import numpy as np
from GLD_server_instance import GLD_server_instance
#import logging



# logging.basicConfig(level=logging.DEBUG,
#                     format='[%(levelname)s] (%(threadName)-10s) %(message)s',
#                     )

D = GLD_server_instance();
D.do_NLDN = False
D.return_JSON = False

# (tighter bounds for search)
D.window_delta = dt.timedelta(0,0,0,0,1,0) # 30 seconds
D.lat_lim = [-200,200]
D.lon_lim = [-100,100]



D.plottime = dt.datetime(2015,03,20,00,00,00)
#stoptime = dt.datetime.now() - dt.timedelta(0,0,0,0,5,0)
print "Starting at " + D.plottime.isoformat()

fb3_file = open('Flyover_Log_FB3_small.txt','a')
fb4_file = open('Flyover_Log_FB4_small.txt','a')

interval_counter = D.plottime

#while (D.plottime < stoptime):
while(1):
	D.log_sightings(fb3_file=fb3_file, fb4_file=fb4_file)
	print D.plottime
	# print "fb3: "+ str(counts_fb3) + ' ' + str(peak_fb3)
	# print "fb4: "+ str(counts_fb4) + ' ' + str(peak_fb4)

	D.plottime = D.plottime +  D.window_delta # dt.timedelta(0,30) # Man I don't understand timedeltas either
												# +  dt.timedelta(0,0,0,0,1,0) #( this is 1 minute))


	#if D.plottime - interval_counter >= dt.timedelta(0,0,0,0,0,1): # 1 hour

	#	print D.plottime
	#	interval_counter = D.plottime

	if D.plottime > (dt.datetime.utcnow() - dt.timedelta(0,0,0,0,5,0)):
		#print "waiting 1 minute"
		time.sleep(60);

	# if (counts_fb3 > 0) or (counts_fb4 > 0):
	# 	print D.plottime
	# 	# f.write(D.plottime.isoformat() + '\tfb3:' + '\t ' + str(D.Firebird_3.coords[1]) + '\t'
	# 	# 				+ str(D.Firebird_3.coords[0]) + str(counts_fb3) + '\t' + str(peak_fb3)
	#  # 				  											 +'\tfb4:' + '\t' + str(D.Firebird_4.coords[1]) + '\t'
	# 	# 				+ str(D.Firebird_4.coords[0]) + str(counts_fb4) + '\t' + str(peak_fb4) + '\r\n')
	# f.write('%s\tfb3:\t%3.3f\t%3.3f\t%d\t%d\tfb4:\t%3.3f\t%3.3f\t%d\t%d\r\n' % 
	# 	(D.plottime.isoformat(),  D.Firebird_3.coords[1],  D.Firebird_3.coords[0], counts_fb3, peak_fb3,
	# 														D.Firebird_4.coords[1],  D.Firebird_4.coords[0], counts_fb4, peak_fb4))

fb3_file.close()	# polite
fb4_file.close()