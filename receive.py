import sys
import bitstring
from rflib import *
from struct import *

d = RfCat();
d.setFreq(315000000) #433920000 for camaro
d.setMdmModulation(MOD_ASK_OOK)
d.makePktFLEN(250)
d.setMdmDRate(4000) #8000 for camaro
d.setMaxPower()
d.lowball()
#results = d.RFlisten()

while True:
	try:
		y,z=d.RFrecv()
		capture = y.encode('hex')
		print capture
	except ChipconUsbTimeoutException:
		pass

#print(results)
