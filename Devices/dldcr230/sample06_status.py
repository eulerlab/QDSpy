###########################################################################################################################################################################
# Texas Instruments DLP LightCrafter 230NP EVM Python Support Code - sample06_status.py - Last Updated June 4th, 2020
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
        This script provides a printout of all status registers provided by the DLPDLCR230NP EVM.
        Registers read are as follows:
            > Short Status
            > System Status
            > Communication Status
            > System Software Version
            > Controller Device ID
            > DMD Device ID
            > Flash Build Version
            > FPGA Version
            > FPGA Status
        Please review the DLPC3436 Programmer's Guide for more information.
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
        if(gpio_init_enable): 
            InitGPIO()
        # ##### ##### Command call(s) start here ##### #####  

        print("Reading DLPC3436 Status Registers...")
        time.sleep(1)
        
        Summary, ShortStatus = ReadShortStatus()      
        print("----------------------")
        print("Short Status Register:")
        PrintRegister(ShortStatus)
        if(Summary.Successful==False):
            print("Read Command Failure")

        Summary, SystemStatus = ReadSystemStatus()
        print("----------------------")
        print("System Status Register:")
        PrintRegister(SystemStatus)
        if(Summary.Successful==False):
            print("Read Command Failure")

        Summary, CommunicationStatus = ReadCommunicationStatus()
        print("----------------------")
        print("Communication Status Register:")
        PrintRegister(CommunicationStatus)
        if(Summary.Successful==False):
            print("Read Command Failure")

        Summary, PatchVersion, MinorVersion, MajorVersion = ReadSystemSoftwareVersion()
        print("----------------------")
        print("System Software Version Register:")
        print ("'Version': ",MajorVersion,".",MinorVersion,".",PatchVersion )
        if(Summary.Successful==False):
            print("Read Command Failure")

        Summary, ControllerDeviceId = ReadControllerDeviceId()
        print("----------------------")
        print("Controller Device ID Register:")
        PrintRegister(ControllerDeviceId)
        if(Summary.Successful==False):
            print("Read Command Failure")

        Summary, DeviceId = ReadDmdDeviceId(DmdDataSelection.DmdDeviceId)
        print("----------------------")
        print("DMD Device ID Register:")
        print ("'Device ID': ", hex(DeviceId) )
        if(Summary.Successful==False):
            print("Read Command Failure")

        Summary, PatchVersion, MinorVersion, MajorVersion = ReadFirmwareBuildVersion()
        print("----------------------")
        print("Flash Build Version Register:")
        print ("'Version': ",MajorVersion,".",MinorVersion,".",PatchVersion )
        if(Summary.Successful==False):
            print("Read Command Failure")

        Summary, FpgaVersion, FpgaEcoRevision, FpgaArmSwVersion = ReadFpgaVersion()
        print("----------------------")
        print("FPGA Version Register:")
        print ("'Version': ",hex(FpgaVersion),"'Eco Revision': ",hex(FpgaEcoRevision),"'ARM SW Version': ",hex(FpgaArmSwVersion) )
        if(Summary.Successful==False):
            print("Read Command Failure")

        Summary, FpgaXprMode, PassFail = ReadFpgaStatus()
        print("----------------------")
        print("FPGA Status Register:")
        print ("'XPR Status': ", FpgaXprMode.value,"'Pass/Fail Status': ", PassFail.value)
        if(Summary.Successful==False):
            print("Read Command Failure")



        # ##### ##### Command call(s) end here ##### #####
        i2c.terminate()


if __name__ == "__main__" : main()


