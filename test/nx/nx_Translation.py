
#This script requires that the devellopement tool of NX is installed on the computer in the following path: C:/SPLM/NX2306/NXBIN/managed
#And the server.dll file is started in NX using CTRL+U

#This script is an example of how to use the NxOpen library in Python to translate a part in NX.

#Import the necessary libraries
from dataclasses import dataclass
import struct
import clr
import sys
import math as m
import time

#Use clr to import the necessary libraries from C++ to Python
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

# Variables

#Identity matrix
rotIndentity = NXOpen.Matrix3x3()
rotIndentity.Xx = 1
rotIndentity.Xy = 0
rotIndentity.Xz = 0
rotIndentity.Yx = 0
rotIndentity.Yy = 1
rotIndentity.Yz = 0
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

#Main loop
while(True):
                
        #Get the active view
        view = theSession.Parts.Display.Views.GetActiveViews()
        
        #Angle of the rotation
        Ax = 0
        Ay = 0
        Az = 0

        #Convert the angular values to radians
        Rx = Ax*m.pi/180
        Ry = Ay*m.pi/180
        Rz = Az*m.pi/180

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
        x = 1
        y = 1
        translation = NXOpen.Point3d(origin.X+x, origin.Y+y, 0)

        #Calculate the scale
        zoom = 0.0
        scale = view[0].Scale + zoom
        if scale < 0.1:
            scale = 0.1
            
        #print(rotMatrix)
        #print(translation)
        #print(scale)

        #Set the rotation, translation and scale
        view[0].SetRotationTranslationScale(rotMatrix, translation, scale)
        
        #Test
        #view[0].Orient(rotMatrix)
        #view[0].Concatenate(translation)
        #view[0].ZoomAboutPoint(scale, vecNull, NXOpen.Point3d(origin.X, origin.Y, 0))
        
        #Update the display
        view[0].UpdateDisplay()
        
        #Wait
        time.sleep(0.1)
    