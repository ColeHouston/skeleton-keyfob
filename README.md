# Skeleton Keyfob
A tool in Python used with the Yardstick One to perform replay and rolling code attacks, specifically on cars.
.cs8 or .c16 sound files with locks, unlocks, etc. wanted for more models of cars to add functionality.

# Installation
It is recommended to use Ubuntu with this tool as it contains some of the correct dependencies to use with RfCat.  The tool has been created and tested on Ubuntu 18.04 and works with Python 2.7.  You can find additional info such as updating Yardstick One firmware and how to get RfCat to work [here](https://github.com/atlas0fd00m/rfcat)


# Jamming
In order to jam frequencies, I used a Raspberry Pi 0 with [rpitx](https://github.com/F5OEO/rpitx) by F5OEO.  It has a cronjob set to run @reboot that will run sendiq to send a jamming file (Can make one by recording a yardstick one that's transmitting 0xfffffff. I recorded with the HackRF but an RTL-SDR works too.).  The jamming file is sent at 0.5 MHz higher than whatever code being captured, but this is all based on preference and what works.  If you have trouble getting clean codes with skeleton-keyfob while jamming at 0.5 Mhz higher, experiment with lowering the frequency used with recording on skeleton keyfob/highering the jamming frequency/creating a less 'noisy' jamming file.  With the cronjob and rpitx it is possible to have a headless raspi that can jam frequencies just by being turned on and is unplugged to stop jamming.

Start your jammer before running 'sudo python skeleton-keyfob.py rolljam', then when the capture is stopped it will prompt you to stop your jammer.  Stop jamming and press enter to continue and transmit your first code. 

# Usage
The 'replay' attack with this tool just listens with the specified settings for everything and upon stopping the capture it will replay everything it captures once.

The 'rolljam' attack is meant to be used with any jammer (hackrf, extra yardstick, raspberry pi, etc) to capture codes and replay them once jamming is completed.  Rolljam will automatically replay the first valid code captured when stopping the capture, then ask if you would like to transmit more codes or exit and save the remaining codes to a file.

The -r / --receive flag is meant to receive codes and upon stopping the capture it will write all codes to a file.

The -t / --transmit flag is used to transmit the first code from a file and remove that code from the file afterwards (can be used with -c / --car to filter out valid codes)

The -c / --car flag can be used with the value 'list' to list all supported cars, and otherwise can be used with supported cars to either filter out codes in a list to only ones for that car and change what action those codes will perform for certain cars.  Over time support for more makes/models/years will be added

All modes of operation can be used with -f to set frequency, -m to set modulation (MOD_ASK_OOK or MOD_2FSK), -b to set baudrate, and -s to set the number of samples that'll be captured before being prompted to continue

# Examples
### Replay attack
sudo python skeleton-keyfob.py replay
### Record codes to file
sudo python skeleton-keyfob.py rolljam -r file.txt
### Transmit code from file (can be used with -c)
sudo python skeleton-keyfob.py rolljam -t file.txt
### Rolljam attack (can be used with -c)
sudo python skeleton-keyfob.py rolljam

# Help page
<pre>

usage: skeleton-keyfob.py [-h] [-b BAUDRATE] [-f FREQUENCY] [-m MODULATION]
                          [-s SLEEP] [-c CAR] [-r RECEIVE] [-t TRANSMIT]
                          {replay,rolljam}

Replay and rolljam attacks against car key fobs with the yardstick one. Jammer
for rolljam not included; check README.md for options and usage

positional arguments:
  {replay,rolljam}      Replay: Capture everything on a certain frequency and
                        replay it upon pressing enter. | Rolljam: Capture
                        codes and replay the first automatically. Saves
                        remaining codes to use later, and for certain cars
                        these can be altered (Use rolljam with -r or -t to
                        save to/transmit from a file)

optional arguments:
  -h, --help            show this help message and exit
  -b BAUDRATE, --baudrate BAUDRATE
                        Default=4800 | Set how quickly bits are read and
                        transferred
  -f FREQUENCY, --frequency FREQUENCY
                        Default=315mhz | Set the frequency to receive and
                        transmit on
  -m MODULATION, --modulation MODULATION
                        Default=ASK_OOK | Set type of (de)modulation
  -s SLEEP, --sleep SLEEP
                        Default=20 | Changes how many codes are captured
                        before being asked to continue
  -c CAR, --car CAR     Specify a supported car type for extra functionality.
                        Can be used with --transmit. Use -c list to see all
                        supported cars (rolljam)
  -r RECEIVE, --receive RECEIVE
                        Receive radio frequencies and log to file (rolljam)
  -t TRANSMIT, --transmit TRANSMIT
                        Transmit a code from a file. Can be used with --car to
                        change the single code (rolljam)

</pre>

