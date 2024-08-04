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
import paho.mqtt.client as mqtt

PLATFORM_WINDOWS = platform.system == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError

broker_address   = "broker.hivemq.com"
topic_root       = "qds"
UUID             = 'd6d09beb68a3448aa0d44747386e3fef'

# ---------------------------------------------------------------------
def on_publish(client, userdata, mid, reason_code, properties):
    # reason_code and properties will only be present in MQTTv5. It's always unset in MQTTv3
    try:
        userdata.remove(mid)
    except KeyError:
        print("on_publish() is called with a mid not present in unacked_publish")
        print("This is due to an unavoidable race-condition:")
        print("* publish() return the mid of the message sent.")
        print("* mid from publish() is added to unacked_publish by the main thread")
        print("* on_publish() is called by the loop_start thread")
        print("While unlikely (because on_publish() will be called after a network round-trip),")
        print(" this is a race-condition that COULD happen")
        print("")
        print("The best solution to avoid race-condition is using the msg_info from publish()")
        print("We could also try using a list of acknowledged mid rather than removing from pending list,")
        print("but remember that mid could be re-used !")

unacked_publish = set()
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_publish = on_publish

mqttc.user_data_set(unacked_publish)
mqttc.connect(broker_address)
mqttc.loop_start()

# Our application produce some messages
sCmd = "load"
fNameStim = "dome_optokinetic_1"
msg = f"{sCmd},{fNameStim}"
tpc = f"{topic_root}/{UUID}"
msg_info = mqttc.publish(tpc, msg, qos=1)
unacked_publish.add(msg_info.mid)

# Due to race-condition described above, the following way to wait for all publish is safer
msg_info.wait_for_publish()

mqttc.disconnect()
mqttc.loop_stop()

# ---------------------------------------------------------------------
