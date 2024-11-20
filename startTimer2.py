#
# File: startTimer2.py
#
# This is updated version of startTimer that has a GUI
# based on the Pi 7" touch screen display and usee PySimpleGUI
#

import time
import PySimpleGUI as sg

import pifacerelayplus

# the enums for system state starint/racing/finishing
# note resetting returns the state to Init
Init = 0 # initalised and waiting start
Starting =  False # in the start sequence
Racing =  False # elaped time shown
Finishing = 3 # if horn sounded at time to finish list
hornOn = False
#started = False # started yes/no
racing = False
sysState = "Prep" # the initial state

def_start = 300
startTime = 300
prevSecs = 0.0 # previous epoch time

fin_list = []

times_col = [ [sg.Text(size=(8, 1), justification='right', font=('Helvetica', 52), text_color='red', key='rtime') ],
          [sg.Text(size=(24, 1), justification='right', font=('Helvetica', 18), text_color='black', key='stime') ] ]

finishers_col = [[sg.Text("List of finishers", text_color='black')],
              [sg.Listbox(fin_list, enable_events=False, size=(35, 10), key="finishers")] ]

# racetime is red to start with 
''' COMMENTED OUT
layout = [[sg.Text('{club logo}', size=(20,1), font=('Helvetica', 24)),
           sg.Text('WARNING', size=(9,1), justification='center',key='warning'),
           sg.Text('PREP', size=(6,1), justification='center',key='prep'),
           sg.Text('HORN', size=(6,1), justification='center',key='horn'),
          [sg.Text('State: '), sg.Text(justification='left', text_colour='black', key='sstate')],
          [sg.Text(size=(8, 1), justification='right', font=('Helvetica', 52), text_color='red', key='rtime') ],
          [sg.Text(size=(24, 1), justification='right', font=('Helvetica', 18), text_color='black', key='stime'),
           sg.Text(size=(10,1), justification='center',key='timercnt') ],
          [sg.Button('Start/Stop'), sg.Button('Incr'), sg.Button('Decr'), sg.Button('Horn'), sg.Button('Finish'), sg.Button('Reset')]]
'''
layout = [[sg.Text('{club logo}', size=(20,1), font=('Helvetica', 24)),
           sg.Text('WARNING', size=(9,1), justification='center',key='warning'),
           sg.Text('PREP', size=(6,1), justification='center',key='prep'),
           sg.Text('HORN', size=(6,1), justification='center',key='horn'),
           sg.Text(size=(10,1), justification='center',key='timercnt') ],
          [sg.Text('State: ',text_color='black'), sg.Text(justification='left', text_color ='black', key='sstate')],
          [sg.Column(times_col),
           sg.VSeperator(),
           sg.Column(finishers_col)],
          [sg.Button('Start/Stop'), sg.Button('Incr'), sg.Button('Decr'), sg.Button('Horn'), sg.Button('Finish'), sg.Button('Reset')]]


# PiFace Relay+
pfr = pifacerelayplus.PiFaceRelayPlus(pifacerelayplus.RELAY)
pfr.relays[0].turn_off()

#
# turn horn on/off - can't parameterise this so need two functions
def soundHorn(): # run out of sequence as 'long_operation()'
    pfr.relays[0].turn_on()
    time.sleep(1)
    pfr.relays[0].turn_off()
# end soundHorn

def soundLongHorn():
    pfr.relays[0].turn_on()
    time.sleep(2.5)
    pfr.relays[0].turn_off()
# end soundHorn

def updateState(state):
    global sysState

    sysState = state
    window['sstate'].update(sysState)  # output the final string
# updateState

# added finalize so elements can be updated before read() is called
window = sg.Window('Start Timer2', layout, default_button_element_size=(10,3), auto_size_buttons=False, use_default_focus=False, finalize=True)

# change the background for the listbox - dark blue 3?
window['finishers'].Widget.config(background='#64778d')
#window['finishers'].Widget.config(background='grey')

#layout = [ [sg.Text('Hello, world!')] ]
#window = sg.Window('Hello Example', layout)

#systime = "13:41:44"
racetime = "05:00" # 'string' for initial state

ctime = time.time() # so we have the 'seconds'
prevSecs = ctime
utime = time.localtime(ctime) # returns struct
systime = f"{utime[3]:02d}:{utime[4]:02d}:{utime[5]:02d}"

# set the initial values
window['sstate'].update(sysState)  # output the final string
window['stime'].update(systime)  # output the final string
window['rtime'].update(racetime)  # output the final string

finishers = 0
# try setting this outside the loop
timerId = window.timer_start(1000, repeating=True)
timerCnt = 0.0

while True:
    # set 'clock' timer
    #window.timer_start(1000, repeating=False)

    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Finish':
        if (event == 'Finish'):
            # guard to ensure init or stopped
            if not Starting and not Racing:
                break
        else:
            widow.timer_stop_all()
            break

    if event == 'Finish':
        if Racing: # then note the time
            finishers += 1

            ctime = time.time()
            utime = time.localtime(ctime) # returns struct
            fintime = f"{utime[3]:02d}:{utime[4]:02d}:{utime[5]:02d}"
            # following add's an hour
            utime = time.localtime(startTime) # returns struct
            elptime = f"{utime[3]:02d}:{utime[4]:02d}:{utime[5]:02d}"
            # now add to list of times
            # add elapsed time which is just the startTime

            fstr = f"{finishers:02d}: {fintime} - {elptime}"
            # add finish time
            fin_list.append(fstr)
            window['finishers'].update(fin_list)

    if event == 'Start/Stop': # this is the button not the state!

        #window['Incr'].update(disabled=True)
        #window['Decr'].update(disabled=True)
        if (Starting == False and Racing == False):
             Starting = True
             #sysState = "Starting"
             updateState("Starting")

             # turn on warning light - orange
             #window['warning'].update(font=('Helvetica', 11, 'underline'))
             window['warning'].update(background_color = 'orange')
             # sound horn to initiate start of race seq
             #window['horn'].update(font=('Helvetica', 11, 'underline'))
             window['horn'].update(background_color = 'red')
             window.perform_long_operation(soundHorn, '-HORN DONE-')

             window['Incr'].update(disabled=True)
             window['Decr'].update(disabled=True)
        elif Starting == True or Racing == True:
             #sysState = "Stop"
             updateState("Stop")
             Starting = False
             Racing = False
  
        '''
        if sysState == "Prep":
            window['Incr'].update(disabled=True)
            window['Decr'].update(disabled=True)
            sysState = "Starting"
        elif sysState == "Starting":
            window['Incr'].update(disabled=False)
            window['Decr'].update(disabled=False)
            sysState = "Stop"
        elif sysState == "Stop":
            window['Incr'].update(disabled=True)
            window['Decr'].update(disabled=True)
            sysState = "Starting"
        '''
        # following is redundant - remove
        window['sstate'].update(sysState)  # output the final string

    # sound the horn - we ignore the event
    if event == 'Horn':
        # turn horn on
        #hornOn = True
        # set text to highlight 'on'
        window['horn'].update(background_color = 'red')
        #window['horn'].update(font=('Helvetica', 11, 'bold'))
        #window['horn'].update(font=('Helvetica', 11, 'underline'))
        window.perform_long_operation(soundHorn, '-HORN DONE-')

    if event == '-HORN DONE-':
        hornOn = False
        #window['horn'].update(font='normal')
        #window['horn'].update(font=('Helvetica', 11, 'normal'))
        window['horn'].update(background_color = 'grey')
        # change text field ?


    if event == 'Incr':
        if startTime < def_start * 3:
            startTime += 300
        #racetime = "10:00"
    if event == 'Decr':
        if startTime >= def_start * 2:
            startTime -= 300
        #racetime = "05:00"

    if event == 'Reset':
        # reset only if not starting or racing
        if not Starting and not Racing: 
            startTime = def_start
            updateState("Prep")
            #sysState = "Prep"
            finishers = 0

            # reset lights - all off

            window['prep'].update(background_color = 'grey')
            window['warning'].update(background_color = 'grey')

            #window['sstate'].update(sysState)  # output the final string

            window['rtime'].update(text_color='red')  # colour

            window['Incr'].update(disabled=False)
            window['Decr'].update(disabled=False)

    # this gets called a lot!
    if event == sg.EVENT_TIMER: # timer event
        timerCnt += 1
        window['timercnt'].update(timerCnt)  # note
        #if TimerCnt
        #systime = "13:41:47"
        ctime = time.time() # so we have the 'seconds'
        utime = time.localtime(ctime) # returns struct

        # has time has progressed?
        if (ctime - prevSecs > 1.0):
            systime = f"{utime[3]:02d}:{utime[4]:02d}:{utime[5]:02d}"
            prevSecs = ctime

            if Starting:
                if startTime > 0:
                    startTime -= 1
                elif Racing == False:
                    # change field to green!
                    window['rtime'].update(text_color='blue')  # colour
                    window['horn'].update(background_color = 'red')
                    window.perform_long_operation(soundHorn, '-HORN DONE-')
                    # turn off warning light - orange
                    #window['warning'].update(font=('Helvetica', 11, 'normal'))
                    window['warning'].update(background_color = 'grey')
                    #sysState = "Racing"
                    updateState("Racing")
                    Starting = False
                    Racing = True
            elif Racing:
                startTime += 1

            # add lights
            # sound horn at 4min and 1min
            if Starting and startTime == 240:
                window['horn'].update(background_color = 'red')
                #window['horn'].update(font=('Helvetica', 11, 'underline'))
                window.perform_long_operation(soundHorn, '-HORN DONE-')
                # turn on prep - blue
                window['prep'].update(background_color = 'blue')
                #window['prep'].update(font=('Helvetica', 11, 'underline'))
            if Starting and startTime == 60:
                #window['horn'].update(font=('Helvetica', 11, 'underline'))
                window['horn'].update(background_color = 'red')
                window.perform_long_operation(soundLongHorn, '-HORN DONE-')
                # turn off prep - blue
                #window['prep'].update(font=('Helvetica', 11, 'normal'))
                window['prep'].update(background_color = 'grey')

    # set racetime
    t_hr = int(startTime/3600)
    t_min = int((startTime - (t_hr * 3600))/60)
    t_sec = int(startTime - (t_hr * 3600) - (t_min * 60))
    if Starting:
        racetime = f"{t_min:02d}:{t_sec:02d}"
    elif Racing: # Racing
        racetime = f"{t_hr:02d}:{t_min:02d}:{t_sec:02d}"
    else:
        racetime = f"{t_min:02d}:{t_sec:02d}"

    # always update the race and system time
    window['stime'].update(systime)  # output the final string
    window['rtime'].update(racetime)  # output the final string

window.close()

# end of startTimer2
