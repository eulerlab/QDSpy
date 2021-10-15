

$ sudo apt-get install python-dev libusb-1.0-0-dev libudev-dev
$ sudo pip install --upgrade setuptools
$ sudo pip install hidapi

download the respective whl file from
https://pypi.org/project/hidapi/#files
and extract it into QDSpy/Devices

sudo pip install pyqt5
sudo pip install numpy
pip install pyglet==1.4.10
sudo pip install moviepy
pip install psutil
sudo pip install pyserial

Troubleshooting
if:
"qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found."
try
sudo apt install libxcb-xinerama0
