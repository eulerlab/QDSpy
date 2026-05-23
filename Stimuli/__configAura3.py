from qds.devices.aura3 import Aura3


a3 = Aura3()
a3.connect("COM3")

a3.setTTLInputs(True, False)

a3.setChannels([0,0,0], [0,5,2])
a3.logChannels()
print("done")
