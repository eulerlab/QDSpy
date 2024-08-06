#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test program for MQTT version of QDSpy

Copyright (c) 2024 Thomas Euler
All rights reserved.

2024-08-03 - Initial version
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import platform
import sys
import paho.mqtt.client as mqtt
import Libraries.mqtt_globals as mgl

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError

# ---------------------------------------------------------------------
def on_publish(client, userdata, mid, reason_code, properties):
    # reason_code and properties will only be present in MQTTv5. It's always unset in MQTTv3
    try:
        userdata.remove(mid)
    except KeyError:
        print("ERROR: `mid` not present in unacked_publish")
    
# ---------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # If no command line argument, exit
        print("No arguments")
        sys.exit()

    # Initialize MQTT client
    unacked_publish = set()
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_publish = on_publish

    # Connect to MQTT broker
    mqttc.user_data_set(unacked_publish)
    mqttc.connect(mgl.broker_address)
    mqttc.loop_start()

    # Convert command line arguments
    msg = ",".join(sys.argv[1:])
    tpc = f"{mgl.topic_root}/{mgl.UUID}"
    print(tpc, msg)

    msg_info = mqttc.publish(tpc, msg, qos=1)
    unacked_publish.add(msg_info.mid)

    # Rest of the code...
    # for all publish is safer
    msg_info.wait_for_publish()

    mqttc.disconnect()
    mqttc.loop_stop()

# ---------------------------------------------------------------------
