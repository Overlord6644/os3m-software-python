
#To use the hid library, you must put the hidapi.dll file in the same directory as the python executable. (C:\Users\username\AppData\Local\Programs\Python\Python310)
#You can find the hidapi.dll in the following github repository: https://github.com/libusb/hidapi

#This code read data from a USB HID device, save it in a CSV and plot it in real time using the matplotlib library in Python.

#Import the necessary libraries
import hid
from dataclasses import dataclass
import dataclasses
import struct
import time
import csv
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


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

# Plotting
style.use('fivethirtyeight')
figure, axis = plt.subplots(2, 3, figsize=(10, 10))
ms, x, y, z, Rx, Ry, Rz = [], [], [], [], [], [], []

    
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
    offset = hid_data(0 ,offset.x/100, offset.y/100, offset.z/100, offset.Rx/100, offset.Ry/100, offset.Rz/100)
    print(offset)
    i = input("Do you want to apply the tare? y/n")
    if i == 'y':
        return offset
    else:
        return hid_data(0, 0, 0, 0, 0, 0, 0)

# Open the csv file
def open_csv(filename, fields):
    
    csvfile = open(dir+filename, 'w', newline='', encoding='utf8')
    print("sep=;", file=csvfile)
    
    # creating a csv dict writer object
    writer = csv.DictWriter(csvfile, dialect='excel', delimiter=";", fieldnames=fields)

    # writing headers (field names)
    writer.writeheader()
    return writer
    
# Log the data
def logData(writer, h):
    
    global start, oldtime
    
    if time.perf_counter_ns()/1000000 - start - oldtime >= interval:
        
        ms = time.perf_counter_ns()/1000000 - start
        data = read_device(h)
        data.time = ms
        
        writer.writerow(dataclasses.asdict(data))
        
        oldtime = ms
        return data

# Animation function for the plot
def animate(i):
    
    global ms, x, y, z, Rx, Ry, Rz
    
    data = logData(writer, h)
    
    ms.append(data.time)
    x.append(data.x)
    y.append(data.y)
    z.append(data.z)
    Rx.append(data.Rx)
    Ry.append(data.Ry)
    Rz.append(data.Rz)
    
    #Limit the axis to the last 100 samples
    ms = ms[-100:]
    x = x[-100:]
    y = y[-100:]
    z = z[-100:]
    Rx = Rx[-100:]
    Ry = Ry[-100:]
    Rz = Rz[-100:]
    
    #Plot layout
    axis[0, 0].clear()
    axis[0, 0].plot(ms, x)
    axis[0, 0].set_title('X')
    
    axis[0, 1].clear()
    axis[0, 1].plot(ms, y)
    axis[0, 1].set_title('Y')
    
    axis[0, 2].clear()
    axis[0, 2].plot(ms, z)
    axis[0, 2].set_title('Z')

    axis[1, 0].clear()
    axis[1, 0].plot(ms, Rx)
    axis[1, 0].set_title('Rx')
    
    axis[1, 1].clear()
    axis[1, 1].plot(ms, Ry)
    axis[1, 1].set_title('Ry')

    axis[1, 2].clear()
    axis[1, 2].plot(ms, Rz)
    axis[1, 2].set_title('Rz')

# Main
h = open_device(vid, pid)
if h:
    print("Connected to device")
else:
    print("Could not connect to device")
    exit()

# Print 3 samples to see if the device is stable
for i in range(3):
    print(read_device(h))
    
# User input
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
    
    # Plotting
    start = time.perf_counter_ns()/1000000
    oldtime = 0
    
    ani = animation.FuncAnimation(figure, animate, interval=500)
    
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    
    plt.title("Axis Value Data logger")
    plt.show()

elif i == 'n':
    exit()
