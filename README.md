os3m-software-python
========================

This project is a rework of the already existing os3m-software coded in C++.
https://github.com/spoter368/os3m-software

This repo aim to implement the OS3M Mouse in python for different CAO Software

Currently this repo is in a state of "proof of concept" and the main implementation is inside the TEST folder of the repo and only for Siemens NX for the HEIA-FR University of Fribourg, Switzerland

---------------

## Installation

This project was built on VSCODE using the VENV envirronement for python.

It was built on the 3.8 Python version.

To run the different scripts you will need to:

1) Create the VENV and install the necessary libraries using the ">Python: Creat Environment" command in VSCode and the requirements.txt file.

2) Copy the hidapi.dll file from the hidapi library in the same directory as the python executable. E.g : "C:\Users\username\AppData\Local\Programs\Python\Python310"
You can find the hidapi.dll in the following github repository: https://github.com/libusb/hidapi
Or use the file in the hidapi-win folder in the repo.

3) For each specific CAO Software a different setup will be needed.
    * If you have Siemens NX:
    You will need to install the devellopement tools for NX to install the NxOpen API files on your computer
    For the specific case of the HEIA-FR the NxOpen files need to be in the following folder "C:/SPLM/NX2306/NXBIN/managed"

---------------

## License

[MIT](https://choosealicense.com/licenses/mit/)
