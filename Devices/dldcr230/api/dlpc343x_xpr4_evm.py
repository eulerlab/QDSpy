###########################################################################################################################################################################
# Texas Instruments DLP LightCrafter 230NP EVM Python Support Code - dlpc343x_xpr4_evm.py - Last Updated May 27th, 2020
# This script is intended to be used with the DLPDLCR230NP EVM on a Raspberry Pi 4 (or compatible)
# It is recommended to consult the DLPDLCR230NPEVM User's Guide for more detailed information on the operation of this EVM
# For technical support beyond what is provided in the above documentation, direct inquiries to TI E2E Forums (http://e2e.ti.com/support/dlp)
###########################################################################################################################################################################
import struct
import time

from enum import Enum

import sys, os.path
python_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(python_dir)

'''
This module cycles provides basic functionality for the DLPDLCR230NP EVM.
To adjust the default GPIO drive strength, set a value below.
GPIO drive strength 5-7 is recommended.
'''

gpio_drive_strength = 5

def PrintRegister(ReadData):
    '''
    Helper function; prints the contents of a register data block read via I2C.
    '''
    filtered_dict = [ (key, value) for key, value in vars(ReadData).items() if not (key.startswith("__") and key.endswith("__"))]
    print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in filtered_dict) + "}")

def InitGPIO():
    '''
    Initializes the GPIO pins on the Raspberry Pi for use with the DLPDLCR230NP EVM in Video mode.
    Standard GPIO functionality is as follows:
    BCM #0  - 21 --> ALT2            (RGB666 DPI Output)
    BCM #22 - 23 --> I2C-7           (SW-based I2C Bus)
    BCM #24      --> SPI_SELECT_ASIC (Flash select line, Tri-Stated for Video mode)
    BCM #25      --> RGB_BUFFER_SEL  (RGB666 Buffer Enable, Drive High for Video mode)
    BCM #26      --> SPI_SELECT_FPGA (Flash select line, Tri-Stated for Video mode)
    NOTE: Do NOT attempt to enable RGB666 buffers and access ASIC/FPGA flash devices simultaneously. Damage to flash devices may occur.
    '''
    print("Initializing Raspberry Pi Default Settings for DLPC3436...")
    os.system("raspi-gpio set 0 op pn")
    os.system("raspi-gpio set 1-27 ip pn")
    time.sleep(1)
    ''' TE 2024-07-25
        Not sure how that ever worked; wrong command? 
        In any case, the drive strength seems not to be critical here
    os.system("gpio drive 0 {0}".format(gpio_drive_strength))
    '''
    os.system("raspi-gpio set 22 op pn")
    os.system("raspi-gpio set 23 op pn")
    os.system("raspi-gpio set 0-21 a2 pn")
    os.system("raspi-gpio set 25 op dh")
    time.sleep(1)


if __name__ == "__main__" : main()



