import sys
import bitstring
from rflib import *
from struct import *

#binL = results.binLength
#freq = results.baseFreq
#baudRate = results.baudRate

d = RfCat()
#wrap in function
#d.setModeIDLE()
d.setFreq(315000000)
d.setMdmModulation(MOD_ASK_OOK)
d.setMdmDRate(4000)
#d.setMdmSyncMode(0)
#d.setMdmChanSpc(240000)
d.setMaxPower()
#end function

d.makePktFLEN(len(str(sys.argv[1])))
d.RFxmit(str(sys.argv[1]))
