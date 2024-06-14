
#To use the hid library, you must put the hidapi.dll file in the same directory as the python executable. (E.g : "C:\Users\username\AppData\Local\Programs\Python\Python310")
#You can find the hidapi.dll in the following github repository: https://github.com/libusb/hidapi

#This code is a simple example of how to read data from a USB HID device using the hid library in Python.

#Import the necessary libraries
import hid
from dataclasses import dataclass
import numpy as np
import struct

#Dataclass for the hid data
@dataclass
class hid_data:
    x: float
    y: float
    z: float
    Rx: float
    Ry: float
    Rz: float

#Variables

#VID and PID of the USB HID device
vid = 0x0483
pid = 0x572b

#Tare variable
tare = False
tare_data = hid_data(0, 0, 0, 0, 0, 0)

# Open the device using the VID, PID,
def open_device(vid, pid):
    try:
        h = hid.Device(vid, pid)
        return h
    except IOError as ex:
        print("Error: {0}".format(ex))
        return None
    
# Close the device
def close_device(h):
    h.close()

# Read USB HID date from the device
def read_device(h):
    try:
        #Read the data in the form of a short (16 bits) from the device
        short = struct.unpack('hhhhhh', h.read(12))
        data = hid_data(short[0]-tare_data.x, short[1]-tare_data.y, short[2]-tare_data.z, short[3]-tare_data.Rx, short[4]-tare_data.Ry, short[5]-tare_data.Rz)
        return data
    except IOError as ex:
        print("Error: {0}".format(ex))
        return None

#Tare the device
def tare_device(h):
    offset = hid_data(0, 0, 0, 0, 0, 0)
    for i in range(1000):
        short = struct.unpack('hhhhhh', h.read(12))
        offset = hid_data(offset.x + short[0], offset.y + short[1], offset.z + short[2], offset.Rx + short[3], offset.Ry + short[4], offset.Rz + short[5])
    offset = hid_data(offset.x/1000, offset.y/1000, offset.z/1000, offset.Rx/1000, offset.Ry/1000, offset.Rz/1000)
    print(offset)
    i = input("Do you want to apply the tare? y/n")
    if i == 'y':
        return offset
    else:
        return hid_data(0, 0, 0, 0, 0, 0)
    

#Main code
h = open_device(vid, pid)
if h:
    print("Connected to device")
#Loop
while(True):
    if tare == False:
        i = input("Do you want to tare the device? (y/n)")
        if i == 'y':
            tare_data = tare_device(h)
            tare = True
            print("Tared")
        elif i == 'n':
            tare = True
    print(read_device(h))