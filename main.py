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

    parser.add_argument("-c", "--car", action="store", type=str, help="Specify a supported car type for extra functionality. Use -c list to see all supported cars (rolljam)")
    parser.add_argument("-r", "--receive", action="store", type=str, help="Receive radio frequencies and log to file (rolljam)")
    parser.add_argument("-t", "--transmit", action="store", type=str, help="Transmit radio frequencies from a file (rolljam)")
    args = parser.parse_args()
    print(args)

    if args.functions=='replay':
        print("REPLAY")
#        replay(baud, freq, mod) #will receive everything and replay everything upon enter
        exit(0)

    if args.functions=='rolljam':
        print("ROLLJAM")
        if args.receive!=None:
            signal = "tes\n\n\n\ntroll\n1234" #roll_receive(baudrate, frequency, modulation)
            f1 = open(args.receive, "wb")
            f1.write(signal)
            f1.close()
            print("Wrote "+str(len(open(args.receive).readlines()))+" codes to "+args.receive)
            exit(0)

#        if receive and file:
#            file =open("W")
#            file=roll_receive()
#            file.close()
#        elif transmit and file:
#            file =open("R")
#            roll_transmit(file)
#            file.close()
#        elif receive or transmit and not file:
#            print("Must specify a file to use with -r or -t")
#            exit(1)
#        elif car=='list':
#            list()
#        else:
#            print("Recording signals...")
#            signal=roll_receive() #press enter to stop. stopping will automatically replay first code

#            while len(signal)>0:
#                if car == 'CAR':
#                    signal=roll_ #{car}(signal)
                    #ALTER SIGNAL TO REFLECT CODE WANTED. BRUTE FORCING WILL BE INCLUDED IN ROLL_CAR ITSELF

                #print(f'You have [{len(signal)}] signals left.')
#                b=input("Press 'c' to play next signal, 'f' to write remaining signals to a file, or anything else to exit")
#                if b==c:
#                    roll_transmit(signal)
                    #remove first code from file, keep the rest
#                elif b==f:
#                    file=input("File name: ")
#                    f=open(file, "w")
#                    f.write( #restofsignals)
#                    f.close()
#                    exit(0)
#                else:
#                    print("Exiting...")
#                    exit(0)



def replay(frequency, baudrate, modulation):
    print("REPLAY")


def rolljam(frequency, baudrate, modulation):
    print("Start your jammer...")
    #sleep(1)
#    while True:
#        a=input("Would you like to receive or transmit?")
#        if a==receive:
#            signal=rolljam_receive(freq, baud, mod)
#        elif a==transmit:
#            rolljam_transmit(freq, baud, mod, a)


def roll_receive(frequency, baudrate, modulation):
    print("ROLL RECEIVE")
    print("Stop your jammer and press ENTER to attack")
    #regex to find first code in file and transmit it
    #return signal(rest of codes by line)


def roll_transmit(frequency, baudrate, modulation, signal):
    print("ROLL TRANSMIT")
#    for code in signal:
#        print(f'you have {len(signal)} codes left')
#        i=input("Press 't' to transmit code or any other key to exit")
#        if i=='t':
#            transmit()
#        else:
#            exit(0)



def list():
    print("Car List: SUBARU yeet")

def rolljam_subaru(frequency, baudrate, modulation):
    print("SUBARU")
    #rolljam_receive(frequency, baudrate, modulation)
    #open received file
    #regex to filter out codes for subaru
    #input("Would you like to: open (t)runk, (c)ar alarm, (l)ock, (u)nlock")
    #close file, open for writing
    #edit file to append rolling code to command code
    print("special car function")



if __name__ == "__main__":
    main()
