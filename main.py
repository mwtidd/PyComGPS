## Test code for read date/time from gps and update RTC
import machine
import math
import network
import os
import uos
import time
import utime
from machine import RTC
from machine import SD
from machine import Timer
from L76GNSS import L76GNSS
from pytrack import Pytrack
from BluetoothServer import BluetoothServer
import struct
# setup as a station

import gc

time.sleep(2)
gc.enable()

bts = BluetoothServer()

bts.run()


#Start GPS
py = Pytrack()
l76 = L76GNSS(py, timeout=600)
#start rtc
rtc = machine.RTC()
print('Aquiring GPS signal....')
#try to get gps date to config rtc
while (True):
   gps_datetime = l76.get_datetime()
   #case valid readings
   if gps_datetime[3]:
       day = int(gps_datetime[4][0] + gps_datetime[4][1] )
       month = int(gps_datetime[4][2] + gps_datetime[4][3] )
       year = int('20' + gps_datetime[4][4] + gps_datetime[4][5] )
       hour = int(gps_datetime[2][0] + gps_datetime[2][1] )
       minute = int(gps_datetime[2][2] + gps_datetime[2][3] )
       second = int(gps_datetime[2][4] + gps_datetime[2][5] )
       #message = "Current location: {}  {} ; Date: {}/{}/{} ; Time: {}:{}:{}".format(gps_datetime[0],gps_datetime[1], day, month, year, hour, minute, second)
       #print(message)

       rtc.init( (year, month, day, hour, minute, second, 0, 0))
       break

print('RTC Set from GPS to UTC:', rtc.now())

chrono = Timer.Chrono()
chrono.start()
sd = SD()
os.mount(sd, '/sd')
start_time = rtc.now()
filename = "/sd/{}{}{}.txt".format(start_time[0],start_time[1],start_time[2])
print("the filename will be {}".format(filename))

interval = 10

while (True):
    f = open(filename, 'a')
    # print("RTC time start loop : {}".format(rtc.now()))
    start_time = (rtc.now()[4] * 60) + rtc.now()[5]
    coord = l76.coordinates()
    print("$GPGLL>> {} - Free Mem: {}".format(coord, gc.mem_free()))
    coord1 = l76.coordinates1()
    print("$GPGGA>> {} - Free Mem: {}".format(coord1, gc.mem_free()))
    coord2 = l76.get_datetime()
    print("$G_RMC>> {} - Free Mem: {}".format(coord2, gc.mem_free()))
    message = "{} {}".format(coord2[0],coord2[1])
    print(message)
    bts.set_message(message)
    print("writing to file {}".format(filename))
    f.write("{} @ {}\n".format(coord1, rtc.now()))
    f.close()
    print("wrote to file {}".format(filename))
    # print("RTC time finish loop : {}".format(rtc.now()))
    end_time = (rtc.now()[4] * 60) + rtc.now()[5]
    elapsed_time = end_time - start_time
    print("time elapsed : {}".format(elapsed_time))

    if (elapsed_time < interval):
        time.sleep(interval - elapsed_time)
