###########################################################################################################################################################################
# Texas Instruments DLP LightCrafter 230NP EVM Python Support Code - flash_write_controller.py - Last Updated June 4th, 2020
# This script is intended to be used with the DLPDLCR230NP EVM on a Raspberry Pi 4 (or compatible)
# It is recommended to consult the DLPDLCR230NPEVM User's Guide for more detailed information on the operation of this EVM
# For technical support beyond what is provided in the above documentation, direct inquiries to TI E2E Forums (http://e2e.ti.com/support/dlp)
# 
# Copyright (C) 2020 Texas Instruments Incorporated - http://www.ti.com/ 
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: 
# 
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.
# 
# Neither the name of Texas Instruments Incorporated nor the names of its contributors may be used to endorse or promote products derived from this software 
# without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
###########################################################################################################################################################################
import struct
import time

from enum import Enum

import sys, os.path
python_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(python_dir)
from api.dlpc343x_xpr4 import *
from api.dlpc343x_xpr4_evm import *
from linuxi2c import *
import i2c

class Set(Enum):
    Disabled = 0
    Enabled = 1

def main():
        '''
        Writes an input *.img file to the flash device of the DLPDLCR230NPEVM's controller.
        Input image must be 4194304 bytes or smaller in size, and must be in *.img format.
        Input image will be padded to 4194304 bytes before writing to flash device.
        Requires flashrom to be installed to use.
        Usage: <python3 flash_write_controller filename.img>
        '''

        gpio_init_enable = False          # Set to FALSE to disable default initialization of Raspberry Pi GPIO pinouts. TRUE by default.
        i2c_time_delay_enable = False    # Set to FALSE to prevent I2C commands from waiting. May lead to I2C bus hangups with some commands if FALSE.
        i2c_time_delay = 0.8             # Lowering this value will speed up I2C commands. Too small delay may lead to I2C bus hangups with some commands.
        protocoldata = ProtocolData()

        def WriteCommand(writebytes, protocoldata):
            '''
            Issues a command over the software I2C bus to the DLPDLCR230NP EVM.
            Set to write to Bus 7 by default
            Some commands, such as Source Select (splash mode) may perform asynchronous access to the EVM's onboard flash memory.
            If such commands are used, it is recommended to provide appropriate command delay to prevent I2C bus hangups.
            '''
            # print ("Write Command writebytes ", [hex(x) for x in writebytes])
            if(i2c_time_delay_enable): 
                time.sleep(i2c_time_delay)
            i2c.write(writebytes)       
            return

        def ReadCommand(readbytecount, writebytes, protocoldata):
            '''
            Issues a read command over the software I2C bus to the DLPDLCR230NP EVM.
            Set to read from Bus 7 by default
            Some commands, such as Source Select (splash mode) may perform asynchronous access to the EVM's onboard flash memory.
            If such commands are used, it is recommended to provide appropriate command delay to prevent I2C bus hangups.
            '''
            # print ("Read Command writebytes ", [hex(x) for x in writebytes])
            if(i2c_time_delay_enable): 
                time.sleep(i2c_time_delay)
            i2c.write(writebytes) 
            readbytes = i2c.read(readbytecount)
            return readbytes

        # ##### ##### Initialization for I2C ##### #####
        # register the Read/Write Command in the Python library
        DLPC343X_XPR4init(ReadCommand, WriteCommand)
        i2c.initialize()
        # ##### ##### Command call(s) start here ##### #####

        filename = sys.argv[-1]
        if not filename.endswith(".img"):
            print("Provide an image file to use. Usage: <python3 flash_write_controller imagename.img>")
            exit(1)
        
        if os.path.getsize(filename)>4194304:
            print("Filesize of image is too large. File size limit: 4194304 bytes")
            exit(1)
       
        # Input file must be zero-padded to 4Mb
        os.system("truncate -s 4194304 {0}".format(filename))        

        print("Initializing Raspberry Pi Default Settings for DLPC3436...")
        time.sleep(1)

        print("DO NOT disconnect EVM or Raspberry Pi during flash write...")
        time.sleep(3)

        print("Resetting GPIO control pins...")
        os.system("raspi-gpio set 0 op pn")
        os.system("raspi-gpio set 1-27 ip pn")
        time.sleep(1)

        print("Setting GPIO drive strength to 5 (0-7, 3 default)...")
        os.system("gpio drive 0 5")
        time.sleep(1)

        print("Putting DLPC3436 to sleep...")
        os.system("raspi-gpio set 26 op dh")
        time.sleep(2)

        print("Initializing SPI bus...")
        os.system("sudo modprobe spi_bcm2835")
        os.system("sudo modprobe spidev")
        os.system("raspi-gpio set 8 op pn")
        os.system("raspi-gpio set 9-11 a0 pn")
        time.sleep(1)

        print("Connecting to DLPC3436 flash device...")
        os.system("raspi-gpio set 24 op dh")
        time.sleep(1) 

        print("Writing image to DLPC3436 flash device... (DO NOT DISCONNECT EVM OR POWER DOWN SYSTEM)")
        os.system("flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed=3000 -w {0}".format(filename))
        os.system("raspi-gpio set 24 ip pn")
        time.sleep(1)

        print("Completing write...")
        os.system("raspi-gpio set 0 op pn")
        os.system("raspi-gpio set 1-27 ip pn")
        time.sleep(5)

        print("Rebooting controller...")
        os.system("raspi-gpio set 26 op dh")
        time.sleep(3)

        print("Resetting GPIO control pins...")
        os.system("raspi-gpio set 0 op pn")
        os.system("raspi-gpio set 1-27 ip pn")
        time.sleep(1)

        print("All done! (execute [init_parallel_mode.py] to initalize video output from Raspberry Pi...)")
        # ##### ##### Command call(s) end here ##### #####
        i2c.terminate()


if __name__ == "__main__" : main()


