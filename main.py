import argparse
import os
import sys
import bitstring
from rflib import *
from struct import *

def main():
    parser = argparse.ArgumentParser(description="Replay and rolljam attacks against car key fobs with the yardstick one. Jammer for rolljam not included; check readme for options and usage")
    parser.add_argument("replay", help="Capture everything on a certain frequency and replay it upon pressing enter")
    parser.add_argument("rolljam", help="Use with -r or -t to either capture signals to a file or play signals from a file.  Use with -c to specify a supported car")

    parser.add_argument("-b", "--baudrate", action="store", type=str, default="4000", help="Set how quickly bits are read and transferred")
    parser.add_argument("-f", "--frequency", action="store", type=str, default="315000000", help="Set the frequency to receive and transmit on")
    parser.add_argument("-m", "--modulation", action="store", type=str, default="MOD_ASK_OOK", choices="['MOD_ASK_OOK, MOD_2FSK']", help="Set type of (de)modulation between frequency and amplitude shift keying")

    parser.add_argument("-c", "--car", action="store", type=str, help="Specify a supported car type for extra functionality.  Use -c list to see all supported cars")
    parser.add_argument("-r", "--receive", action="store", type=str, help="S")
    parser.add_argument("-t", "--transmit", action="store", type=str, help="S")


    if replay:
        replay(baud, freq, mod)

    if rolljam and car and transmit:
        rolljam_car()

    if rolljam and car and transmit:
        rolljam_car()

    if rolljam and -t:
        rolljam_transmit(baud, freq, mod)

    if rolljam and -r:
        rolljam_receive(baud, freq, mod)




def replay(frequency, baudrate, modulation):
    print("REPLAY")


def rolljam():
    print("ROLLJAM")


def spec_car():
    if "-c" set:
        if "--list" set:
            print("supported car list")
        else:
            print("HACKS")
    else:




if __name__ == "__main__":
    main()
