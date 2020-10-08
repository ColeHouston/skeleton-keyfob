import argparse
import os
import sys
import bitstring
from rflib import *
from struct import *

def main():
    parser = argparse.ArgumentParser(description="Replay and rolljam attacks against car key fobs with the yardstick one. Jammer for rolljam not included; check README.md for options and usage")
    parser.add_argument("functions", choices=['replay', 'rolljam'], help="Capture everything on a certain frequency and replay it upon pressing enter") #parser.add_argument("rolljam", help="Use with -r or -t to either capture signals to a file or play signals from a file. Use with -c to specify a supported car")

    parser.add_argument("-b", "--baudrate", action="store", type=str, default="4000", help="Set how quickly bits are read and transferred")
    parser.add_argument("-f", "--frequency", action="store", type=str, default="315000000", help="Set the frequency to receive and transmit on")
    parser.add_argument("-m", "--modulation", action="store", type=str, default="MOD_ASK_OOK", help="Set type of (de)modulation")

    parser.add_argument("-c", "--car", action="store", type=str, help="Specify a supported car type for extra functionality. Can be used with --transmit. Use -c list to see all supported cars (rolljam)")
    parser.add_argument("-r", "--receive", action="store", type=str, help="Receive radio frequencies and log to file. Replays one code upon ending recording (rolljam)")
    parser.add_argument("-t", "--transmit", action="store", type=str, help="Transmit a code from a file. Can be used with --car to change the single code (rolljam)")
    args = parser.parse_args()

    if args.car=='list':
        list()
        exit(0)

    if args.functions=='replay':
        print("REPLAY")
#        replay(args.baudrate, args.frequency, args.moduldation) #will receive everything and replay everything upon enter
        exit(0)

    if args.functions=='rolljam':
        #exits if attempt made to receive and transmit at same time
        if args.receive!=None and args.transmit!=None:
            print("You must choose between receiving or transmitting")
            exit(1)

        #records codes and writes to file, tells how many codes written
        elif args.receive!=None:
            signal = "test\nlines"                                               #roll_receive(args.baudrate, args.frequency, args.modulation)
            f1 = open(args.receive, "wb")
            f1.write(signal)
            f1.close()
            print("Wrote "+str(len(open(args.receive).readlines()))+" codes to "+args.receive)
            exit(0)

        #transmits a code either for a specific car (user can change code then)
        #or just transmit next code in file (removes first line of file)
        elif args.transmit!=None:
            #check if file exists
            f1 = open(args.transmit, "rb")
            if args.car!=None:
                if args.car=="subaru":
                    signal=rolljam_subaru(f1)
                else:
                    print("Car not found")
                    exit(1)
            updated_file=roll_transmit(args.baudrate, args.frequency, args.modulation, signal)
            exit(0)

        else:
            rolljam(args.frequency, args.baudrate, args.modulation, args.car)



def replay(frequency, baudrate, modulation):
    print("REPLAY")


def rolljam(frequency, baudrate, modulation, car):
    print("Start your jammer...")
    #sleep(1)
    signal=roll_receive(frequency, baudrate, modulation)
    print("[+] Received "+str(len(signal.splitlines()))+" codes")

    print("Stop jamming...")
    #sleep(1)
    roll_transmit(frequency, baudrate, modulation, signal[0])
    #remove first code from signal
    i="i"
    while i!="e" and len(signal)>0:
        i = input("You have "+str(len(signal.splitlines()))+" codes left.\nWhat would you like to do? (t)ransmit  (e)xit: ")

        if i=="t":
            if car=="subaru":
                new_signal = roll_subaru(signal)
                #replace first code in signal with new_signal
            roll_transmit(frequency, baudrate, modulation, signal)
            #remove first code from signal

        elif i=="e":
            saving = input("Would you like to save the remaining codes? (y)es  (n)o: ")
            if saving == ("y" or "yes"):
                filename = ("./"+input("File name: "))
                f_end = open(filename, "wb")
                f_end.write(signal)
                f_end.close()

    if len(signal)==0:
        print("[-] Ran out of codes")
    else:
        print("[+] Exiting")
    exit(0)


#receives til user hits enter, then sorts codes out separated by newlines
def roll_receive(frequency, baudrate, modulation):
    print("ROLL RECEIVE")
    #regex to filter out junk
    #return signal(separate found codes by line)


#transmits one code
def roll_transmit(frequency, baudrate, modulation, signal):
    print("ROLL TRANSMIT")
    #code=signal[0]
    #transmit code


#prints list of supported cars
def list():
    print("Car List: \n\nSubaru - tested on 2010 subaru impreza")


#filters to just codes for subaru impreza (2010),
#then allows user to change first code in file
def rolljam_subaru(signal):
    print("SUBARU")
    #open received list of codes
    #regex to filter to just codes for subaru
    #input("Would you like to: open (t)runk, (c)ar alarm, (l)ock, (u)nlock")
    #new_signal=code of choice+part of first line in file
    #return new_signal



if __name__ == "__main__":
    main()
