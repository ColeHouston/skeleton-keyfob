# skeleton-keyfob
A tool in Python used with the Yardstick One to perform replay and rolling code attacks, specifically on cars.
.cs8 or .c16 sound files with locks, unlocks, etc. wanted for more models of cars to add functionality.

# Usage
The 'replay' attack with this tool just listens with the specified settings for everything and upon stopping the capture it will replay everything it captures once.
The 'rolljam' attack is meant to be used with any jammer (hackrf, extra yardstick, raspberry pi, etc) to capture codes and replay them once jamming is completed.  Rolljam will automatically replay the first valid code captured when stopping the capture, then ask if you would like to transmit more codes or exit and save the remaining codes to a file.


The -r / --receive flag is meant to receive codes and upon stopping the capture it will write all codes to a file.
The -t / --transmit flag is used to transmit the first code from a file and remove that code from the file afterwards (can be used with -c / --car to filter out valid codes)

The -c / --car flag can be used with the value 'list' to list all supported cars, and otherwise can be used with supported cars to either filter out codes in a list to only ones for that car and change what action those codes will perform for certain cars.  Over time support for more makes/models/years will be added



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

