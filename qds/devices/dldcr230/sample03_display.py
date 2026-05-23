###########################################################################################################################################################################
# Texas Instruments DLP LightCrafter 230NP EVM Python Support Code - sample03_display.py - Last Updated June 4th, 2020
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
        This script cycles through available display options on the DLPDLCR230NPEVM.
        Raspberry Pi automatically configures each display setting via I2C.
        System will await user input before cycling through each test pattern.
        Display commands executed include:
            > Display Image Orientation
            > Display Image Curtain
            > Display Border Color
            > Image Freeze Enable/Disable
            > Mirror Lock Enable/Disable
            > Keystone
            > Local Area Brightness Boost (LABB)
            > Content-Adaptive Illumination Control (CAIC)
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
		

        print("Cycling Display Settings on DLPC3436...")
        Summary = WriteDisplayImageCurtain(1,Color.Black)
        Summary = WriteSourceSelect(Source.ExternalParallelPort, Set.Disabled)
        Summary = WriteInputImageSize(1920, 1080)
        Summary = WriteExternalVideoSourceFormatSelect(ExternalVideoFormat.Rgb666)
        time.sleep(1)
        Summary = WriteDisplayImageCurtain(0,Color.Black)

        print("Cycling Image Orientation Settings...")
        Summary = WriteDisplayImageOrientation(ImageFlip.ImageNotFlipped,ImageFlip.ImageNotFlipped)
        time.sleep(2)
        Summary = WriteDisplayImageOrientation(ImageFlip.ImageNotFlipped,ImageFlip.ImageFlipped)
        time.sleep(2)
        Summary = WriteDisplayImageOrientation(ImageFlip.ImageFlipped,ImageFlip.ImageNotFlipped)
        time.sleep(2)
        Summary = WriteDisplayImageOrientation(ImageFlip.ImageFlipped,ImageFlip.ImageFlipped)
        input("Press ENTER to proceed")
        
        print("Cycling Image Curtain Settings...")
        Summary = WriteDisplayImageCurtain(1,Color.Black)
        time.sleep(1)
        Summary = WriteDisplayImageCurtain(1,Color.Red)
        time.sleep(1)
        Summary = WriteDisplayImageCurtain(1,Color.Green)
        time.sleep(1)
        Summary = WriteDisplayImageCurtain(1,Color.Blue)
        time.sleep(1)
        Summary = WriteDisplayImageCurtain(1,Color.Cyan)
        time.sleep(1)
        Summary = WriteDisplayImageCurtain(1,Color.Magenta)
        time.sleep(1)
        Summary = WriteDisplayImageCurtain(1,Color.Yellow)
        input("Press ENTER to proceed")

        print("Reverting Display Settings...")
        Summary = WriteDisplayImageOrientation(ImageFlip.ImageFlipped,ImageFlip.ImageFlipped)
        Summary = WriteSourceSelect(Source.ExternalParallelPort, Set.Disabled)
        Summary = WriteDisplayImageCurtain(0,Color.Black)
        time.sleep(2)

        print("Performing Image Freeze Test...")
        Summary = WriteImageFreeze(1)
        time.sleep(1)
        for freeze_time in range(1,5+1):
            print("Unfreezing in",6-freeze_time,"seconds...")
            time.sleep(1)
        Summary = WriteImageFreeze(0)
        input("Press ENTER to proceed")

        print("Performing Mirror Lock Test...")
        Summary = WriteDisplayImageCurtain(1,Color.Black)
        time.sleep(1)
        Summary = WriteMirrorLock(MirrorLockOptions.DmdInterfaceLock)
        for lock_time in range(1,5+1):
            print("Unlocking Mirrors in",6-lock_time,"seconds...")
            time.sleep(1)
        Summary = WriteMirrorLock(MirrorLockOptions.DmdInterfaceUnlock)
        Summary = WriteDisplayImageCurtain(0,Color.Black)
        input("Press ENTER to proceed")

        print("Performing Keystone Test...")
        WriteKeystoneCorrectionControl(1,1.5,1,0)
        for pitch_angle in range(0,30):
            WriteKeystoneProjectionPitchAngle(pitch_angle)
            time.sleep(1)
        WriteKeystoneCorrectionControl(0,0,0,0)
        input("Press ENTER to proceed")

        print("Performing LABB Test...")
        WriteLocalAreaBrightnessBoostControl(LabbControl.Automatic,  1,  1)
        input("Press ENTER to proceed")
        WriteLocalAreaBrightnessBoostControl(LabbControl.Disabled,  1,  1)
        WriteKeystoneCorrectionControl(Set.Disabled,  0,  0,  0)

        print("Performing CAIC Test...")
        Summary, CaicSettings = ReadCaicImageProcessingControl()
        CaicSettings.CaicWpcControl = CaicWpcControl.Disabled
        CaicSettings.CaicColorModulationControl = CaicModulationControl.Independent
        CaicSettings.CaicGainControl = CaicGainControl.P1024
        CaicSettings.CaicGainDisplayEnable = True
        Summary = WriteCaicImageProcessingControl(CaicSettings)
        Summary = WriteLedOutputControlMethod(LedControlMethod.Automatic)
        input("Press ENTER to proceed")
        Summary = WriteLedOutputControlMethod(LedControlMethod.Manual)

        # ##### ##### Command call(s) end here ##### #####
        i2c.terminate()


if __name__ == "__main__" : main()


