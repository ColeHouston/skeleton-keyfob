#!/usr/bin/env python2

import sys
import os
from rflib import *
import argparse

parser = argparse.ArgumentParser(description="Yard Stick One utility to record, modify, and send keyfob signals.", version="0.1")
parser.add_argument('-f', action="store", default="433920000", dest="baseFreq",help='Target frequency to listen for (default 433920000)',type=int)
parser.add_argument('-r', action="store", dest="baudRate",default=4800,help='Baudrate, defaults to 4800',type=int)
parser.add_argument('-n', action="store", dest="numSignals",default=3,help='Number of signals to capture before replaying',type=int)
parser.add_argument('-i', action="store", default="24000", dest="chanWidth",help='Width of each channel (lowest being 24000 -- default)',type=int)
parser.add_argument('-o', action="store", default="", dest="outFile",help='output file to save to')
parser.add_argument('-p', action="store", default="100", dest="power",help='Power level for re-transmitting',type=int)
parser.add_argument('-m', action="store", default="-100", dest="minRSSI",help='Minimum RSSI db to accept signal',type=int)
parser.add_argument('-c', action="store", default="60000", dest="chanBW",help='Channel BW for RX',type=int)
results = parser.parse_args()

raw_capture = []
# RFCat Configuration

# Quit if not running as root. As RfCat requires root
if os.geteuid() != 0:
    exit("You need to have root privileges to use RfCat.")
    
d = RfCat()
d.setMdmModulation(MOD_ASK_OOK)
d.setFreq(results.baseFreq)
d.setMdmSyncMode(0)
d.setMdmDRate(results.baudRate)
d.setMdmChanBW(results.chanBW)
d.setMdmChanSpc(results.chanWidth)
d.setChannel(0)
d.setPower(results.power)
d.lowball(1)

print("Searching for a fob...")

while True:
    try:		
	y, t = d.RFrecv(1)
	sampleString = y.encode('hex')
	#print sampleString
	strength = 0 - ord(d.getRSSI())
	
	#sampleString = re.sub(r'((f)\2{8,})', '',sampleString)
	if (re.search(r'((0)\2{15,})', sampleString)):
	    print "Signal Strength:" + str(strength)
	    if(strength > results.minRSSI):
		raw_capture.append(sampleString)
		print "Found " + str(sampleString)
		if(len(raw_capture) >= results.numSignals):
		    break;

    except ChipconUsbTimeoutException:
	pass
    except KeyboardInterrupt:
	break

print("raw_capture:", raw_capture)
d.setModeIDLE()
