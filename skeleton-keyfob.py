import argparse
import os
import sys
import time
import bitstring
from rflib import *
from struct import *

def main():
    parser = argparse.ArgumentParser(description="Replay and rolljam attacks against car key fobs with the yardstick one. Jammer for rolljam not included; check README.md for options and usage")
    parser.add_argument("functions", choices=['replay', 'rolljam'], help="Replay: Capture everything on a certain frequency and replay it upon pressing enter.  Rolljam: Capture codes and replay the first automatically. Saves remaining codes to use later, and for certain cars these can be altered (Use rolljam with -r or -t to save to/transmit from a file)")

    parser.add_argument("-b", "--baudrate", action="store", type=str, default="4000", help="Set how quickly bits are read and transferred")
    parser.add_argument("-f", "--frequency", action="store", type=str, default="315000000", help="Set the frequency to receive and transmit on")
    parser.add_argument("-m", "--modulation", action="store", type=str, default="MOD_ASK_OOK", help="Set type of (de)modulation")

    parser.add_argument("-c", "--car", action="store", type=str, help="Specify a supported car type for extra functionality. Can be used with --transmit. Use -c list to see all supported cars (rolljam)")
    parser.add_argument("-r", "--receive", action="store", type=str, help="Receive radio frequencies and log to file (rolljam)")
    parser.add_argument("-t", "--transmit", action="store", type=str, help="Transmit a code from a file. Can be used with --car to change the single code (rolljam)")
    args = parser.parse_args()

    if args.car=='list':
        list()
        exit(0)

    if args.functions=='replay':
        replay(args.frequency, args.baudrate, args.modulation)
        exit(0)

    if args.functions=='rolljam':
        #exits if attempt made to receive and transmit at same time
        if args.receive!=None and args.transmit!=None:
            print("You must choose between receiving or transmitting")
            exit(1)

        #records codes and writes to file, tells how many codes written
        elif args.receive!=None:
            signal = "test\nlines\ngo\nbrrrr"
            #signal = roll_receive(args.frequency, args.baudrate, args.modulation)
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
            rolljam(args.frequency, args.baudrate, args.modulation, args.car)



def replay(frequency, baudrate, modulation):
    print("REPLAY")


def rolljam(frequency, baudrate, modulation, car):
    print("Start your jammer...")
    time.sleep(1)
    signal=roll_receive(frequency, baudrate, modulation)
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
def roll_receive(frequency, baudrate, modulation):
    print("ROLL RECEIVE")
    #regex to filter out junk
    signal="test\nreceive\nfunction\none\ntwo"
    #if 0 codes received:
        #print("[-] Received 0 codes")
    return signal  #(separate found codes by line) DO NOT SPLIT. just have \n's


#transmits one code
def roll_transmit(frequency, baudrate, modulation, code):
    print("ROLL TRANSMIT")
    #code is a single line out of signal
    #will probably have to convert code into bits before transmitting and stuff
    #transmit code


#prints list of supported cars
def list():
    print("Car List: \nSubaru - tested on 2010 subaru impreza")


#filters to just codes for subaru impreza (2010),
#then allows user to change first code in file
def rolljam_car(car, code):
    c = raw_input("Would you like to: open (t)runk, (p)anic alarm, (l)ock, (u)nlock ")
    #WILL PROB HAVE TO CONVERT TO BITS TO FIGURE OUT PREFIX+CODE, THEN BACK TO HEX
    if car=="subaru":
        print("SUBARU")
        #code = regex to filter to just codes for subaru
        if c=="l":
            prefix="lock"
            #new_code = prefix + code.parseoutprefix
        elif c=="u":
            prefix="unlock"
            #new_code = prefix + code.parseoutprefix
        elif c=="t":
            prefix="trunk"
            #new_code = prefix + code.parseoutprefix
        elif c=="p":
            prefix="panic"
            #new_code = prefix + code.parseoutprefix
    else:
        print("[-] Car not supported")
        exit(1)
    if c!="l" and c!="u" and c!="t" and c!="p":
        print("[-] Unknown command, code will remain unchanged.")
        new_code=code
    new_code=prefix+code  #testing code
    return new_code



if __name__ == "__main__":
    main()
