
#To use the hid library, you must put the hidapi.dll file in the same directory as the python executable. (C:\Users\username\AppData\Local\Programs\Python\Python310)
#You can find the hidapi.dll in the following github repository: https://github.com/libusb/hidapi

##This code read data from a USB HID device and save it in a CSV.

#Import the necessary libraries
import hid
from dataclasses import dataclass
import dataclasses
import struct
import time
import csv
import os


#Dataclass for the hid data
@dataclass
class hid_data:
    time: float
    x: float
    y: float
    z: float
    Rx: float
    Ry: float
    Rz: float

# Variables
vid = 0x0483
pid = 0x572b
tare = False
tare_data = hid_data(0, 0, 0, 0, 0, 0, 0)
interval = 10

#Csv file
fields = ['time', 'x', 'y', 'z', 'Rx', 'Ry', 'Rz']
dir = os.getcwd()+"/test/Datalogger/"
filename = "temp_Log.csv"

    
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
        short = struct.unpack('hhhhhh', h.read(12))
        data = hid_data(0 ,short[0]-tare_data.x, short[1]-tare_data.y, short[2]-tare_data.z, short[3]-tare_data.Rx, short[4]-tare_data.Ry, short[5]-tare_data.Rz)
        return data
    except IOError as ex:
        print("Error: {0}".format(ex))
        return None

#Tare the device
def tare_device(h):
    offset = hid_data(0, 0, 0, 0, 0, 0, 0)
    for i in range(100):
        short = struct.unpack('hhhhhh', h.read(12))
        offset = hid_data(0 ,offset.x + short[0], offset.y + short[1], offset.z + short[2], offset.Rx + short[3], offset.Ry + short[4], offset.Rz + short[5])
    offset = hid_data(0 ,offset.x/1000, offset.y/1000, offset.z/1000, offset.Rx/1000, offset.Ry/1000, offset.Rz/1000)
    print(offset)
    i = input("Do you want to apply the tare? y/n")
    if i == 'y':
        return offset
    else:
        return hid_data(0, 0, 0, 0, 0, 0, 0)

#Open a csv file
def open_csv(filename, fields):
    csvfile = open(dir+filename, 'w', newline='', encoding='utf8')
    print("sep=;", file=csvfile)
    
    # creating a csv dict writer object
    writer = csv.DictWriter(csvfile, dialect='excel', delimiter=";", fieldnames=fields)

    # writing headers (field names)
    writer.writeheader()
    return writer

#Log data handler
def log_data(writer, data):
    writer.writerow(data)

#Log thread
def log_thread(writer, h):
    start = time.perf_counter_ns()/1000000
    oldtime = 0
    
    while True:
        
        if time.perf_counter_ns()/1000000 - start - oldtime >= interval:
        
            ms = time.perf_counter_ns()/1000000 - start
            data = read_device(h)
            data.time = ms
            
            log_data(writer, dataclasses.asdict(data))
            
            oldtime = ms

#Main code
h = open_device(vid, pid)
if h:
    print("Connected to device")
else:
    print("Could not connect to device")
    exit()
    
for i in range(3):
    print(read_device(h))
    
i = input("Do you want to start the datalogging process? (y/n)")
if i == 'y':
    i = input("Do you want to tare the device? (y/n)")
    if i == 'y':
        tare_data = tare_device(h)
        tare = True
        print("Tared")
    i = input("What is the name of the file?")
    filename = i + "_log.csv"
    writer = open_csv(filename, fields)
    i = input("What is the interval between samples in ms?")
    interval = int(i)
    print("Starting logging in 3")
    for i in range(3):
        print(".")
        time.sleep(0.25)
    print("2")
    for i in range(3):
        print(".")
        time.sleep(0.25)
    print("1")
    for i in range(3):
        print(".")
        time.sleep(0.25)
    print("Logging")
    log_thread(writer, h)

elif i == 'n':
    exit()
