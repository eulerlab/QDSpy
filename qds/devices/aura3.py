#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lumencor Aura III light engine
Implements a Python class that interfaces with the light engine

Command referend from Lumencor, Inc., www.lumencor.com
Document Number 57-10018, Revision C 103019

Copyright (c) 2025 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ = "thomas.euler@eulerlab.de"

# ---------------------------------------------------------------------
import platform
import serial
from qds.devices.lightsource import LightSource, ErrCodes
from types import FunctionType

PLATFORM_WINDOWS = platform.system() == "Windows"

# fmt: off
StatusCodes = dict([
    (0,   "OK"),
    (1,   "Fan malfunction"),
    (2,   "High temperature (over 25 C)"),
    (3,   "High temperature and fan malfunction"),
    (4,   "Device safety lock active"),
    (5,   "Invalid hardware configuration"),
    (6,   "Standby mode (TECs disabled)"),
    (7,   "TECs warming up    ])")
])

ChannelStatusCodes = dict([
    (0,   "OK"),
    (51,  "Invalid channel index"),
    (56,  "Invalid hardware configuration"),
    (57,  "Channel locked (Unknown reason)"),
    (572, "Channel locked (Fan malfunction)"),
    (571, "Channel locked (Max. temperature exceeded)"),
    (573, "Channel locked (Interlock activated)"),
    (574, "Channel locked (Power supply current limit exceeded)"),
    (58,  "Channel busy (long running operation)"),
    (60,  "Interlock active"),
    (64,  "TEC lock active"),
    (65,  "TEC temperature out of range (temperature control error)")
])     
# fmt: on

# ---------------------------------------------------------------------
class Aura3(LightSource):
    
    def __init__(self, _funcLog :FunctionType =None):
        """ Create and initialize Aura3 light source object """        
        super().__init__(_funcLog)
        self._devInfo["name"] = "Aura3"


    def connect(self, port :str, baud: int =115200):
        """ Connect to Aura3 device at `port`, `baud` """
        try:
            # Try opening a connection to the device
            self._serClient = serial.Serial(port, baud, timeout=1.0)

            # Check if the device replies ...
            self.log("", f"Checking at `{port}` ...")
            self._isReady = self._is_connected()

            if self._isReady:
                # Retrieve channel map
                self._chanMap = []
                tmp = self._get_channel_map()
                pins = self._get_ttl_input_pins()
                for i, ch in enumerate(tmp):
                    self._chanMap.append({
                        "index": i, "ID": ch, 
                        "name": "n/a", "peak_nm" :0,
                        "pin": pins[i]
                    })
                self.updateChannels()    

                # Retrieve device info and status    
                self._devInfo["model"] = self._get_model()[1]
                self._devInfo["version"] = f"v{self._get_version()[1]}"
                self.updateDeviceInfo(log=True)

            else:    
                # Device did not reply
                self.log("ERROR", "No reponse")

        except serial.SerialException:
            # Serial port could not be opened
            self.log("ERROR", f"Could not open `{port}`")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateChannels(self, log :bool =False, limited :bool =False):
        """ Update the internal representation of the channels
        """
        if self._isReady:
            chst = self._get_light_channel_status()
            chon = self._get_light_channel_states()
            chin = self._get_light_channel_intensities()
            chlv = self._get_light_channel_power_levels()
            ches = self._get_light_channel_estim_power_output()
            if not limited:
                chrf = self._get_light_channel_power_ref()
                chrg = self._get_light_channel_power_regulation()
 
            for i in range(len(self._chanMap)):
                self._chanMap[i]["status"] = [
                    chst[i], ChannelStatusCodes[chst[i]]
                ]
                self._chanMap[i]["on"] = chon[i]
                self._chanMap[i]["inten_percent"] = chin[i] /10
                self._chanMap[i]["pow_level"] = chlv[i]
                self._chanMap[i]["pow_estim_mW"] = ches[i]
                if not limited:
                    self._chanMap[i]["pow_ref_mW"] = chrf[i]
                    self._chanMap[i]["pow_reg_enabled"] = chrg[i]                
            if log:
                self.logChanels()    


    def updateDeviceInfo(self, log :bool =False):
        """ Update the internal representation of the system status
        """
        if self._isReady:
            state = self._get_engine_status()
            self._devInfo["status"] = [state, StatusCodes[state]]
            temp = self._get_system_temp()
            self._devInfo["temp_degC"] = temp[0]
            self._devInfo["humid_percent"] = temp[1]
            curr = self._get_supply_current()
            self._devInfo["supply_curr_A"] = curr
            if log:
                self.logDeviceInfo()    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def logChannels(self, chans :list =[]):
        """ Logs the information in `_chanMap` """
        nCh = len(self._chanMap)
        chans = [i for i in range(nCh)] if len(chans) == 0 else chans
        for ich in chans:
            if ich >= 0 and ich < nCh:
                ch = self._chanMap[ich]        
                self.log(
                    "INFO", 
                    f"#{ch["index"]} ID=`{ch["ID"]}/{ch["name"]}`, "
                    f"peak={ch["peak_nm"]} nm, TTL pin={ch["pin"]}"
                )    
                self.log(
                    "", 
                    f"  Status      : {"ON " if ch["on"] else "OFF"}, "
                    f"`{ch["status"][1]}` ({ch["status"][0]})"
                )
                self.log("", f"  Intensity   : {ch["inten_percent"]:.1f} %")
                self.log("", f"  Power level : {ch["pow_level"] /10:.1f} %")
                self.log(
                    "", 
                    f"  Power estim.: {ch["pow_estim_mW"]:.1f} mW "
                    f"(Ref={ch["pow_ref_mW"]:.1f} mW, "
                    f"regulation {"enabled" if ch["pow_reg_enabled"] else "disabled"})"
                )

    
    def logDeviceInfo(self):
        """ Log device info and status """    
        self.log(
            "INFO", 
            f"{self._devInfo["model"]} {self._devInfo["version"]} "
            f"with {len(self._chanMap)} channel(s)"
        )
        self.log(
            "", 
            f"  Status      : `{self._devInfo["status"][1]}`" 
            f"({self._devInfo["status"][0]})"
        )
        self.log(
            "", 
            f"  Environment : {self._devInfo["temp_degC"]:.1f}°C, " 
            f"{self._devInfo["humid_percent"]:.1f}% humidity"
        )
        self.log(
            "", 
            f"  Total curr. : {self._devInfo["supply_curr_A"]:.3f}A" 
        )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setChannels(self, states :list =[], intens :list =[]) -> ErrCodes:
        """ Sets intensities (in %) of individual channels and switches 
        them on or off. Parameters must be provided in the order of 
        channel IDs; -1 means that the respective channel is left unchanged.
        The parameter lists must be the same length as than the channel map.
        """
        # Empty lists become ignore-all lists
        nCh = len(self._chanMap)
        if len(states) == 0:
            states = [-1] *nCh
        if len(intens) == 0:
            intens = [-1] *nCh

        if not(len(states) == nCh and len(intens) == nCh):
            # Parameter list(s) not the same length as channel map
            return ErrCodes.PARAMS_INVALID

        # Make sure that ingored channels are indicated by -1
        states = [-1 if a < 0 else a for a in states]
        intens = [-1 if a < 0 else a for a in intens]

        # Replace -1 by current intensity value and set intensities
        # (intensities in `_chanMap` are percent, whereas the Aura III
        #  requires promille, hence *10)
        curr_intens = [ch["inten_percent"] for ch in self._chanMap]
        for i in range(nCh):
            intens[i] = curr_intens[i] if intens[i] < 0 else intens[i]
            intens[i] *= 10
        self._set_light_channel_intensities(intens)

        # Replace -1 by current state
        curr_states = [ch["on"] for ch in self._chanMap]
        for i in range(nCh):
            states[i] = curr_states[i] if states[i] < 0 else states[i]
        self._set_light_channel_states(states)

        # Retrieve state and intensity
        self.updateChannels(limited=True)
        return ErrCodes.OK
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setTTLInputs(self, enable :bool, positive :bool) -> ErrCodes:
        """ Enable TTL inputs and set polarity 
        """
        res = self._send_cmd(f"SET TTLENABLE {int(enable)}")
        if enable:
            res = self._send_cmd(f"SET TTLPOL {["NEG", "POS"][int(positive)]}")
        return ErrCodes.OK
        
    # -------------------------------------------------------------------
    # Version, model, and status
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _get_version(self, check=True) -> str:
        """ Returns the Light Engine firmware version. """
        return self._send_cmd("GET VER")


    def _get_model(self) -> str:
        """ Returns model name. """
        return self._send_cmd("GET MODEL")
    

    def _get_engine_status(self) -> int:
        """ Returns current status code from the Light Engine. “0” means all OK. 
        Any other number will represent an error ID with a specific meaning
        (see `StatusCodes`)
        """
        res = self._send_cmd("GET STAT")
        return int(res[1]) if res[0] == ErrCodes.OK else None


    def _get_system_temp(self) -> list:
        """ Returns current temperature in degrees Celsius, relative 
        humidity (if appropriate sensor available) and dew point in 
        degrees Celsius (if appropriate sensor is available).
        """
        res = self._send_cmd("GET TEMPDATA")
        tmp = [float(val) for val in res[1].split()]
        return tmp if res[0] == ErrCodes.OK else []
    

    def _get_supply_current(self) -> float:
        """ Read power supply current measurement (in [A])
        """
        res = self._send_cmd("GET SUPPLYCURRENT")
        return float(res[1]) /1000 if res[0] == ErrCodes.OK else None
    
    # -------------------------------------------------------------------
    # Channels
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _get_num_channels(self) -> int:
        """ Returns the number of channels available in the Light Engine. """
        res = self._send_cmd("GET NUMCH")
        return int(res[1]) if res[0] == ErrCodes.OK else 0


    def _get_channel_map(self) -> list:
        """ Returns ordered list of color mnemonics, e.g. VIOLET,BLUE,GREEN,RED, 
        separated by spaces. The first channel ID is 0, the next one 1, etc. 
        The list in this example should be interpreted as zero-based mapping 
        of channel numbers to color mnemonics
        """
        res = self._send_cmd("GET CHMAP")
        return res[1].split() if res[0] == ErrCodes.OK else []


    def _get_light_channel_status(self) -> list:
        """ Obtains multiple light channel status codes with a single 
        command according to the list provided by `get_channel_map`. 
        Channel status codes are provided in the order of channel IDs. 
        (see `ChannelStatusCodes`) 
        """
        res = self._send_cmd("GET MULCHSTAT")
        tmp = [int(val) for val in res[1].split()]
        return tmp if res[0] == ErrCodes.OK else []        


    def _get_ttl_input_pins(self) -> list:
        """ Get TTL input connector pin number (1..15) for all light 
        channels. If a channel doesn't support TTL triggering, or the 
        input connector pin is not defined server will respond with -1 
        (for that channel).
        """
        res = self._send_cmd("GET MULTTLPIN")
        tmp = [int(val) for val in res[1].split()]
        return tmp if res[0] == ErrCodes.OK else []        


    def _get_light_channel_states(self) -> list:
        """ Obtains multiple light channel states with a single command. 
        Channel ON or OFF states (1 or 0) are provided in the order of
        channel IDs.
        """
        res = self._send_cmd("GET MULCH")
        tmp = [int(val) for val in res[1].split()]
        return tmp if res[0] == ErrCodes.OK else []      

    def _set_light_channel_states(self, states :list) -> ErrCodes:
        """ Turns multiple lights ON or OFF with a single command. Channel
        ON or OFF (1 or 0) are provided in the order of channel IDs.
        """
        if len(states) == len(self._chanMap):
            s = " ".join(str(int(val != 0)) for val in states)
            return self._send_cmd(f"SET MULCH {s}")[0]


    def _get_light_channel_intensities(self) -> list:
        """ Obtains multiple light channel current intensities with a 
        single command. Channel intensities (0 to 1000) are provided in 
        the order of channel IDs.
        """
        res = self._send_cmd("GET MULCHINT")
        tmp = [int(val) for val in res[1].split()]
        return tmp if res[0] == ErrCodes.OK else []      

    def _set_light_channel_intensities(self, states :list) -> ErrCodes:
        """ Sets multiple light channel intensities with a single command. 
        Channel intensities (0 to 1000) are provided in the order of 
        channel IDs. If power control is engaged some of the intensity
        values might be ignored.
        """
        if len(states) == len(self._chanMap):
            lim_states = [min(max(val, 0), 1000) for val in states]    
            s = " ".join(str(int(val)) for val in lim_states)
            return self._send_cmd(f"SET MULCHINT {s}")[0]


    def _get_light_channel_power_levels(self) -> list:
        """ Obtains multiple light channel estimated power levels with 
        a single command. Power levels are provided in the order of 
        channel IDs.
        """
        res = self._send_cmd("GET MULCHPWR")
        tmp = [int(val) for val in res[1].split()]
        return tmp if res[0] == ErrCodes.OK else []      


    def _get_light_channel_estim_power_output(self) -> list:
        """ Obtains multiple light channel estimated power output 
        (in mW) with a single command. Power estimation is based on the 
        power output calibration factor, power sensor reading, power 
        sensor exposure, power sensor gain and crosstalk level. 
        Estimation model assumes linear dependency. Power outputs are 
        provided in the order of channel IDs.
        """
        res = self._send_cmd("GET MULCHPWRWATTS")
        tmp = [float(val) for val in res[1].split()]
        return tmp if res[0] == ErrCodes.OK else []      


    def _set_light_channel_power_regulation(self, states :list) -> ErrCodes:
        """ Activate/deactivate power regulation for all channels 
        (per channel control) in a single command. Power regulator 
        adjusts light intensity in order to keep power level at the 
        referent value.
        """
        if len(states) == len(self._chanMap):
            s = " ".join(str(int(val != 0)) for val in states)
            return self._send_cmd(f"SET MULPWRLOCK {s}")[0]

    def _get_light_channel_power_regulation(self) -> list:
        """ Returns the power regulator state (active = 1 / inactive = 0) 
        for all light channels in a single command.
        """
        res = self._send_cmd("GET MULPWRLOCK")
        tmp = [int(val) for val in res[1].split()]
        return tmp if res[0] == ErrCodes.OK else []      


    def _get_light_channel_power_ref(self) -> list:
        """ Returns power reference values (in mW) for all light channels
        in a single command. Value -1 is returned if the power reference 
        hasn't been defined for a specific light channel.
        """
        res = self._send_cmd("GET MULPWRREF")
        tmp = [int(val) for val in res[1].split()]
        return tmp if res[0] == ErrCodes.OK else []      

    '''
    Set Multiple Light Power References (SET MULPWRREF)

    Later:    
    Get Error Description (GET ERRORTEXT)
    Check TTL Inputs Master Switch State (GET TTLENABLE)
    Get Multiple Light TTL States (ON/OFF) (GET MULCHTTL)
    Get Multiple Light Actual States (ON/OFF) (GET MULCHACT)
    '''
    # -------------------------------------------------------------------
    # Helper
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _is_connected(self) -> bool:
        """ Check if the device replies """
        try:
            self._serClient.write(b"GET VER\n")
            return len(self._serClient.readline()) > 0
        except serial.SerialException:
            return False   


    def _send_cmd(self, cmd :str) -> list:
        """ Returns a list with the error code and the reply as string
        (which is empty in case of an error) 
        """
        if not self._isReady:
            self.log("ERROR", "Device is not ready")
            return [ErrCodes.NOT_READY, ""] 

        self._serClient.write(str.encode(cmd +"\n"))
        res = self._serClient.readline().decode()
        if res[0].upper() == "E":
            self.log("ERROR", "Command not recognized")
            return [ErrCodes.COMMAND_UNKNOWN, ""] 

        elif res[0].upper() == "A":
            skip = len(cmd.split()[1]) +3
            return [ErrCodes.OK, res[skip:-2]]
        
        else:
            self.log("ERROR", "Unknown error")
            return [ErrCodes.UNKNOWN_ERROR, ""] 

# ---------------------------------------------------------------------
def start():
    a3 = Aura3()
    a3.connect("COM3")
    return a3

