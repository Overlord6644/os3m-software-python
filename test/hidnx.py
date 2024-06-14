
#To use the hid library, you must put the hidapi.dll file in the same directory as the python executable. (E.g : "C:\Users\username\AppData\Local\Programs\Python\Python310")
#You can find the hidapi.dll in the following github repository: https://github.com/libusb/hidapi

#This script requires that the devellopement tool of NX is installed on the computer in the following path: C:/SPLM/NX2306/NXBIN/managed
#And the server.dll file is started in NX using CTRL+U

#This script reads data from a USB HID device and uses it to rotate, translate and scale the view in NX

#Import the necessary libraries
import hid
from dataclasses import dataclass
import struct
import clr
import sys
import math as m
import time

#Use clr to import the necessary libraries
clr.AddReference('System')
import System
from System import Activator, Type

#Add the path to the NXOpen libraries
sys.path.append("C:/SPLM/NX2306/NXBIN/managed")
clr.AddReference('NXOpen')
import NXOpen

#Data class for the hid data
@dataclass
class hid_data:
    x: float
    y: float
    z: float
    Rx: float
    Ry: float
    Rz: float

#Matrix multiplication
def MatrixMult(m1, m2):
    m = NXOpen.Matrix3x3()
    m.Xx = m1.Xx*m2.Xx + m1.Xy*m2.Yx + m1.Xz*m2.Zx
    m.Xy = m1.Xx*m2.Xy + m1.Xy*m2.Yy + m1.Xz*m2.Zy
    m.Xz = m1.Xx*m2.Xz + m1.Xy*m2.Yz + m1.Xz*m2.Zz
    m.Yx = m1.Yx*m2.Xx + m1.Yy*m2.Yx + m1.Yz*m2.Zx
    m.Yy = m1.Yx*m2.Xy + m1.Yy*m2.Yy + m1.Yz*m2.Zy
    m.Yz = m1.Yx*m2.Xz + m1.Yy*m2.Yz + m1.Yz*m2.Zz
    m.Zx = m1.Zx*m2.Xx + m1.Zy*m2.Yx + m1.Zz*m2.Zx
    m.Zy = m1.Zx*m2.Xy + m1.Zy*m2.Yy + m1.Zz*m2.Zy
    m.Zz = m1.Zx*m2.Xz + m1.Zy*m2.Yz + m1.Zz*m2.Zz
    return m

# Open the device using the VID, PID,
def open_device(vid, pid):
    try:
        h = hid.Device(vid, pid)
        return h
    except IOError as ex:
        print("Error: {0}".format(ex))
        return None

# Read USB HID date from the device
def read_device(h):
    try:
        short = struct.unpack('hhhhhh', h.read(12))
        data = hid_data(short[0]*x_scale, short[1]*y_scale, short[2]*z_scale, short[3]*Rx_scale, short[4]*Ry_scale, short[5]*Rz_scale)
        return data
    except IOError as ex:
        print("Error: {0}".format(ex))
        return None

# Close the device
def close_device(h):
    h.close()



# Variables

# VID and PID of the USB HID device
vid = 0x0483
pid = 0x572b

#Scale for axis
x_scale = 0.001
y_scale = 0.00001
z_scale = 0.001
Rx_scale = 0.0001
Ry_scale = 0.0001
Rz_scale = 0.0001



#Identity matrix
rotIndentity = NXOpen.Matrix3x3()
rotIndentity.Xx = 1
rotIndentity.Xy = 0
rotIndentity.Xz = 0
rotIndentity.Yx = 0
rotIndentity.Yy = 1
rotIndentity.Zx = 0
rotIndentity.Zy = 0
rotIndentity.Zz = 1

#Null vector
vecNull = NXOpen.Point3d(0, 0, 0)

#Init values

#Initial matrix
rotMatrix = rotIndentity

#Initial translation
translation = vecNull

#Initial scale
scale = 1


# Get the type of the remote object
sessionType = Type.GetType("NXOpen.Session, NXOpen")

# Connect to the remote object
theSession = Activator.GetObject(sessionType, "http://127.0.0.1:4567/NXOpenSession")

#Main code

#Open the device
h = open_device(vid, pid)
if h:
    print("Connected to device")
#Loop
while(True):

    #Read the data from the device
    data = read_device(h)
    print(data)

    #Check if the device is moving
    if data.x != 0 or data.y != 0 or data.z != 0 or data.Rx != 0 or data.Ry != 0 or data.Rz != 0:  
        
        #Get the active view
        view = theSession.Parts.Display.Views.GetActiveViews()
        
        #Convert the angular values to radians
        Rx = data.Rx*m.pi/180
        Ry = data.Ry*m.pi/180
        Rz = data.Rz*m.pi/180

        #Calculate the rotation matrix
        rotMatrix.Xx = m.cos(Rz)*m.cos(Ry)
        rotMatrix.Xy = m.sin(Rz)*m.cos(Ry)
        rotMatrix.Xz = -m.sin(Ry)
        rotMatrix.Yx = m.cos(Rz)*m.sin(Ry)*m.sin(Rx) - m.sin(Rz)*m.cos(Rx)
        rotMatrix.Yy = m.sin(Rz)*m.sin(Ry)*m.sin(Rx) + m.cos(Rz)*m.cos(Rx)
        rotMatrix.Yz = m.cos(Ry)*m.sin(Rx)
        rotMatrix.Zx = m.cos(Rz)*m.sin(Ry)*m.cos(Rx) + m.sin(Rz)*m.sin(Rx)
        rotMatrix.Zy = m.sin(Rz)*m.sin(Ry)*m.cos(Rx) - m.cos(Rz)*m.sin(Rx)
        rotMatrix.Zz = m.cos(Ry)*m.cos(Rx)
        
        #Multiply the rotation matrix with the current matrix
        rotMatrix = MatrixMult(view[0].Matrix, rotMatrix)

        #Get the origin of the view
        origin = view[0].Origin
        
        #Calculate the translation
        translation = NXOpen.Point3d(origin.X+data.x, origin.Y+data.z, 0)

        #Calculate the scale
        scale = view[0].Scale - data.y
        if scale < 0.1:
            scale = 0.1
            
        #print(rotMatrix)
        #print(translation)
        #print(scale)
        
        #Set the rotation, translation and scale
        ##TODO: SET SCALE ON ORIGIN OF PART
        view[0].SetRotationTranslationScale(rotMatrix, translation, scale)
        
        #view[0].Orient(rotMatrix)
        #view[0].Concatenate(translation)
        #view[0].ZoomAboutPoint(scale, vecNull, NXOpen.Point3d(origin.X, origin.Y, 0))
        
        #Update the display
        view[0].UpdateDisplay()

        #Wait
        time.sleep(0.1)
    