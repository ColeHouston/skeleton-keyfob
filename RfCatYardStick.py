#!/usr/bin/env python2

import sys
import os
from rflib import *
import argparse

parser = argparse.ArgumentParser(description="Yard Stick One utility to record, modify, and send keyfob signals.", version="0.1")
parser.add_argument('-f', action="store", default="315000000", dest="baseFreq",help='target frequency to listen for (default 315000000)',type=int)
parser.add_argument('-b', action="store", dest="baudRate",default="4000",help='set the baudrate for Rx/Tx (default 4000)',type=int)
#parser.add_argument('-m', action="store", dest="modulation", default="MOD_ASK_OOK", help="set type of demodulation to use (default MOD_ASK_OOK)", type=str)
#parser.add_argument('-n', action="store", dest="numSignals",default=3,help='Number of signals to capture before replaying',type=int)
#parser.add_argument('-i', action="store", default="24000", dest="chanWidth",help='Width of each channel (lowest being 24000 -- default)',type=int)
parser.add_argument('-o', action="store", default='', dest="outFile",help="output file to save codes to")
#parser.add_argument('-p', action="store", default="100", dest="power",help='Power level for re-transmitting',type=int)
#parser.add_argument('-m', action="store", default="-100", dest="minRSSI",help='Minimum RSSI db to accept signal',type=int)
#parser.add_argument('-c', action="store", default="60000", dest="chanBW",help='Channel BW for RX',type=int)
parser.add_argument('-r', action="store", default="false", dest="replay", help="perform a replay attack for static codes, will replay all codes when enter is pressed", type=bool)
parser.add_argument('-R', action="store", default="false", dest="rolljam", help="perform a rolljam attack, can be used generally or for a specific car if also using the -c flag. Will replay one code when enter is pressed", type=bool)
parser.add_argument('-T', action="store", default="false", dest="transmit", help="transmit stored signals from a rolljam attack", type=bool)
parser.add_argument('-c', action="store", default='', dest="carType", help="Specify a supported car to add options when transmitting (subaru, buick)")
results = parser.parse_args()

raw_capture = []
# RFCat Configuration

# Quit if not running as root. As RfCat requires root
if os.geteuid() != 0:
    exit("You need to have root privileges to use RfCat.")

d = RfCat()
d.setMdmModulation(MOD_ASK_OOK)  #(results.modulation)
d.setFreq(315000000)
#d.setMdmSyncMode(0)
d.setMdmDRate(4800)
#d.setMdmChanBW(results.chanBW)
#d.setMdmChanSpc(results.chanWidth)
#d.setChannel(0)
d.setMaxPower() #(results.power)
d.lowball()

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
