
# Description: Main file for the OS3M Mouse Desktop App
#UI Creation using PySimpleGUI for the NxOpen implementation see the TEST folder

import PySimpleGUI as sg

#Supported apps
supportedApps =[
    'SolidWorks',
    'Siemens NX',
    'Fusion360',
]

#App list column
app_list_column = [
    [
        sg.Text('Supported Apps')
    ],
    [
        sg.Listbox(
            supportedApps, enable_events=True, size=(40, 20),
            key='-APP LIST-'
        )
    ],
    [
        sg.Button('Connect', key='-CONNECT-')
    ]
]
#Settings column
settings_column = [
    [
        sg.Text('Mouse Axis Settings')
    ]
]

#full layout
layout = [
    [
        sg.Column(app_list_column),
        sg.VSeparator(),
        sg.Column(settings_column),
    ]
]

#Create the window
window = sg.Window('OS3M Mouse Desktop App', layout, margins=(100, 100))

#Create an event loop
while True:
    event, values = window.read()
    if event == 'Connect' or event == sg.WIN_CLOSED:
        break

#Close the window
window.close()