import crepe
from scipy.io import wavfile
import time
import numpy as np
import win32api, win32con, win32com.client as comclt
import KeyPressing
import pyaudio
import wave
import audioop
from tkinter import *
from threading import Thread
import io #io and sys are for suppressing the crepe default text output
import sys
import os #for file IO

wsh = comclt.Dispatch("WScript.Shell")

global silence, seconds, fs, X1, X2, Low1, Low2, High1, High2, High3, Low3, volume, pitch, midVolume, highVolume, lowPitch, midPitch, highPitch, downArrow, upArrow, dragging, lowVolume, stopLogic, speedLimit, calcmidPitch, mouseLogicTemp, fpsKeysLogicTemp, fpsKeysLogic, veryhighPitch, verylowPitch, mouseLogic, fpsKeysLogic, sensativity, startButtonState, defaults, X
startButtonState, stopLogic, downArrow, upArrow, dragging, silence, X2, Low2, High2, Low3, High3 = 1, False, False, False, False, True, 0, 0, 0, 0, 0
mouseLogic, fpsLogic, fpsKeysLogic, mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp, speedLimit = False, False, False, True, False, False, 40
mouseLogic, fpsLogic, fpsKeysLogic = False, False, False
channels, chunk, fs, seconds = 1, int(1024/2), 16000, .06 #chunks per sample, sample rate, duration of each while loop recording
sample_format = pyaudio.paInt16  # 16 bits per sample
filename = "testfile.wav"

def mouse_logic():
    # Main Logic (only execute logic if noise is above a threshold), start by releasing all keys
    global X1, X2, Low1, Low2, Low3, High1, High2, High3, volume, pitch, midVolume, highVolume, lowPitch, midPitch, highPitch, veryhighPitch, silence, dragging, upArrow, downArrow, speedLimit, calcmidPitch, sensativity
    
    if (volume <= lowVolume):
        actionReadoutText.config(text="Action: N/A")
        if silence == False: #this makes it only release keys the first instant you're silent and not continuosly, making your computer usable if you're quiet
            #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0) #left mouseuse
            silence = True
        if dragging == True:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
            dragging = False
        if upArrow == True:
            upArrow = False
        if downArrow == True:
            downArrow = False

    if (volume > lowVolume):
        if silence == True:
            silence = False
        #Figure out what keys to release
        if (upArrow == False and downArrow == False): # do logic only if not pressing up or down arrow
            if (volume > highVolume): 
                actionReadoutText.config(text="Action: LEFT-CLICK")
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
                #X1 = X2
                #X2 = time.time()
                #if (X2-X1) > 0.20 and (X2-X1) < 0.6: # check for double high (difference between last timestamp you were loud and this time) to see if left mouse should be clicked (release once there's silence again)
                #    actionReadoutText.config(text="Action: DRAGGING")
                #    dragging = True
                #else:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    
            # If Pitch is on lower side of "midpoint"
            elif pitch <= midPitch:
                Low1 = Low2
                Low2 = Low3
                Low3 = time.time()
                if ((Low2-Low1) > 0.20 and (Low2-Low1) < 0.6) and ((Low3-Low2) > 0.25 and (Low3-Low2) < 0.6) and (dragging == False): # check for double low (difference between last timestamp you were low and this time) to see if down arrow should be pressed
                    downArrow = True
                    actionReadoutText.config(text="Action: DOWN ARROW")
                    wsh.SendKeys("{DOWN}")
                    wsh.SendKeys("{DOWN}")
                    time.sleep(0.1)
                elif (pitch <= lowPitch):
                    actionReadoutText.config(text="Action: DRAGGING")
                    dragging = True
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
                else:
                    actionReadoutText.config(text="Action: MOVING MOUSE")
                    if volume-midVolume < speedLimit:
                        for i in range(5): #makes it move more the lower your pitch is
                            KeyPressing.MoveMouse(int(sensativity*2*((pitch-midPitch)/(midPitch-lowPitch))),int(sensativity*.03*(midVolume-volume-10))) #move based on the percentage into the low range you are
                            time.sleep(.015)
                    else:
                        for i in range(5): #makes it move more the lower your pitch is
                            KeyPressing.MoveMouse(int(sensativity*2*((pitch-midPitch)/(midPitch-lowPitch))),int(sensativity*.03*(-speedLimit)))
                            time.sleep(.015)
                                   
            # If Pitch is on higher side of "midpoint"
            else:
                High1 = High2
                High2 = High3
                High3 = time.time()
                if ((High2-High1) > 0.20 and (High2-High1) < 0.6) and ((High3-High2) > 0.25 and (High3-High2) < 0.6) and (dragging == False): #check for double high pitch -- to see if up arrow should be pressed
                    upArrow = True
                    actionReadoutText.config(text="Action: UP ARROW")
                    wsh.SendKeys("{UP}")
                    wsh.SendKeys("{UP}")
                    time.sleep(0.1)
                elif (pitch > highPitch and dragging == False):
                    actionReadoutText.config(text="Action: RIGHT-CLICK")
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
                    time.sleep(.3)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
                    time.sleep(.3)
                else:
                    actionReadoutText.config(text="Action: MOVING MOUSE")
                    if volume-midVolume < speedLimit:
                        for i in range(5): #makes it move more the lower your pitch is
                            KeyPressing.MoveMouse(int(sensativity*2*((pitch-midPitch)/(highPitch-midPitch))),int(sensativity*.03*(midVolume-volume+10))) #move based on the percentage into the high range you are
                            time.sleep(.015)
                    else:
                        for i in range(5): #makes it move more the lower your pitch is
                            KeyPressing.MoveMouse(int(sensativity*2*((pitch-midPitch)/(highPitch-midPitch))),int(sensativity*.03*(-speedLimit)))
                            time.sleep(.015)
        elif upArrow == True:
            actionReadoutText.config(text="Action: UP ARROW")
            wsh.SendKeys("{UP}")
            time.sleep(0.1)
        else:
            actionReadoutText.config(text="Action: DOWN ARROW")
            wsh.SendKeys("{DOWN}")
            time.sleep(0.1)

def fps_logic():
    # Main Logic (only execute logic if noise is above a threshold), start by releasing all keys
    global X1, X2, Low1, Low2, Low3, High1, High2, High3, volume, pitch, midVolume, highVolume, verylowPitch, lowPitch, midPitch, highPitch, veryhighPitch, silence, sensativity
    
    if (volume <= 2):
        actionReadoutText.config(text="Action: N/A")
        if silence == False: #this makes it only release keys the first instant you're silent and not continuosly, making your computer usable if you're quiet
            KeyPressing.ReleaseAll()
        silence = True
    if (volume > 2):
        silence = False
        KeyPressing.ReleaseAll()
        # If Very High Volume
        if (volume > highVolume):
            X1 = X2
            X2 = time.time()
            KeyPressing.ReleaseAll()
            if (X2-X1) > 0.20 and (X2-X1) < 0.6: # check for double high (difference between last timestamp you were loud and this time) for either melee or shoot
                actionReadoutText.config(text="Action: Q")
                KeyPressing.PressKey(0x10) #q
                time.sleep(0.1)
                KeyPressing.ReleaseKey(0x10)
                time.sleep(0.1)
            else:
                actionReadoutText.config(text="Action: LEFT-CLICK")
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    
        # If Pitch is on lower side of "midpoint"
        elif pitch <= midPitch:
            Low1 = Low2
            Low2 = time.time()
            KeyPressing.ReleaseAll()
            if (Low2-Low1) > 0.20 and (Low2-Low1) < 0.6: # check for double low (difference between last timestamp you were low and this time)
                actionReadoutText.config(text="Action: G")
                KeyPressing.PressKey(0x22) #g
            elif pitch <= lowPitch and pitch > verylowPitch:
                actionReadoutText.config(text="Action: E")
                KeyPressing.PressKey(0x12) #e
            elif pitch <= verylowPitch:
                KeyPressing.PressKey(0x13) #r
                actionReadoutText.config(text="Action: R")
            else:
                actionReadoutText.config(text="Action: MOVING MOUSE")
                if volume-midVolume < speedLimit:
                    for i in range(5): #makes it move more the lower your pitch is
                        KeyPressing.MoveMouse(int(sensativity*2*((pitch-midPitch)/(midPitch-lowPitch))),int(sensativity*.03*(midVolume-volume-10))) #move based on the percentage into the low range you are
                        time.sleep(.015)
                else:
                    for i in range(5): #makes it move more the lower your pitch is
                        KeyPressing.MoveMouse(int(sensativity*2*((pitch-midPitch)/(midPitch-lowPitch))),int(sensativity*.03*(-speedLimit)))
                        time.sleep(.015)
                                   
        # If Pitch is on higher side of "midpoint"
        else:
            High1 = High2
            High2 = time.time()
            KeyPressing.ReleaseAll()
            if (High2-High1) > 0.2 and (High2-High1) < 0.6: #check for double high pitch
                actionReadoutText.config(text="Action: SPACEBAR")
                KeyPressing.PressKey(0x39) #spacebar
            elif pitch > highPitch and pitch <= veryhighPitch:
                actionReadoutText.config(text="Action: W")
                KeyPressing.PressKey(0x11) #w
            elif pitch > veryhighPitch:
                actionReadoutText.config(text="Action: SHIFT + W")
                KeyPressing.PressKey(0x2a) #shift
                KeyPressing.PressKey(0x11) #w
            else:
                actionReadoutText.config(text="Action: MOVING MOUSE")
                if volume-midVolume < speedLimit:
                    for i in range(5): #makes it move more the lower your pitch is
                        KeyPressing.MoveMouse(int(sensativity*2*((pitch-midPitch)/(highPitch-midPitch))),int(sensativity*.03*(midVolume-volume+10))) #move based on the percentage into the high range you are
                        time.sleep(.015)
                else:
                    for i in range(5): #makes it move more the lower your pitch is
                        KeyPressing.MoveMouse(int(sensativity*2*((pitch-midPitch)/(highPitch-midPitch))),int(sensativity*.03*(-speedLimit)))
                        time.sleep(.015)
                    time.sleep(.015)

def fps_keys_logic():
    # Main Logic (only execute logic if noise is above a threshold), start by releasing all keys
    global Low1, Low2, Low3, High1, High2, volume, pitch, midVolume, highVolume, verylowPitch, lowPitch, midPitch, highPitch, veryhighPitch, silence
    
    if (volume <= 2):
        actionReadoutText.config(text="Action: N/A")
        if silence == False: #this makes it only release keys the first instant you're silent and not continuosly, making your computer usable if you're quiet
            KeyPressing.ReleaseAll()
        silence = True
    if (volume > 2):
        silence = False
        KeyPressing.ReleaseAll()
        # If Very High Volume
        if (volume > highVolume):
            actionReadoutText.config(text="Action: Q")
            KeyPressing.PressKey(0x10) #q
            time.sleep(0.1)
            KeyPressing.ReleaseKey(0x10)
            time.sleep(0.1)
    
        # If Pitch is on lower side of "midpoint"
        elif pitch <= lowPitch:
            Low1 = Low2
            Low2 = time.time()
            KeyPressing.ReleaseAll()
            if (Low2-Low1) > 0.20 and (Low2-Low1) < 0.6: # check for double low (difference between last timestamp you were low and this time)
                actionReadoutText.config(text="Action: G")
                KeyPressing.PressKey(0x22) #g
            elif pitch <= lowPitch and pitch > verylowPitch:
                actionReadoutText.config(text="Action: E")
                KeyPressing.PressKey(0x12) #e
            else:
                KeyPressing.PressKey(0x13) #r
                actionReadoutText.config(text="Action: R")
                                   
        # If Pitch is on higher side of "midpoint"
        elif pitch >= highPitch:
            High1 = High2
            High2 = time.time()
            KeyPressing.ReleaseAll()
            if (High2-High1) > 0.2 and (High2-High1) < 0.6: #check for double high pitch
                actionReadoutText.config(text="Action: SPACEBAR")
                KeyPressing.PressKey(0x39) #spacebar
            elif pitch > highPitch and pitch <= veryhighPitch:
                actionReadoutText.config(text="Action: W")
                KeyPressing.PressKey(0x11) #w
            else:
                actionReadoutText.config(text="Action: SHIFT + W")
                KeyPressing.PressKey(0x2a) #shift
                KeyPressing.PressKey(0x11) #w

def logicImplementation():
    global volume, pitch, stopLogic, mouseLogicTemp, fpsKeysLogicTemp
    while not(stopLogic):
        ### Audio Recording Code Found from https://realpython.com/playing-and-recording-sound-python/#python-sounddevice_1
        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
        
        frames = []  # Initialize array to store frames
        
        #for i in range(0, int(fs / chunk * seconds)): # Store data in chunks for X seconds
        data = stream.read(chunk)
        frames.append(data)
        volume = audioop.rms(data,2)
        
        volume = int(volume/30)
        stream.stop_stream() # Stop and close the stream 
        stream.close()
        p.terminate() # Terminate the PortAudio interface
        
        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        #CREPE
        text_trap = io.StringIO() # mute crepe output
        sys.stdout = text_trap # mute crepe output
        sr, audio = wavfile.read(filename)
        time1, frequency, confidence, activation = crepe.predict(audio, fs, model_capacity="tiny", viterbi=False, step_size = int(seconds*1000))
        sys.stdout = sys.__stdout__ # restore text output

        pitch = frequency[0] # measured in Hz
        if (volume > 2):
            pitchReadoutText.config(text=("Pitch: "+str(int(pitch)))) #change pitch and volume gui elements
        else:
            pitchReadoutText.config(text=("Pitch: 0")) #change pitch and volume gui elements
        volumeReadoutText.config(text=("Volume: "+str(int(volume))))
        if mouseLogic == True:
            Thread(target = mouse_logic).start()
        elif fpsLogic == True:
            Thread(target = fps_logic).start()
        else:
            Thread(target = fps_keys_logic).start()


############################ MAIN ##############################
# Order of Importance of Actions:
# high volume >> low and high pitches >> everything else
################################################################


if __name__ == '__main__':
    root = Tk()
    root.title("Voice Controls for Mouse and Keyboard")
    root.geometry('600x1000')

    rows = 0
    while rows < 40:
        root.rowconfigure(rows, weight=1)
        root.columnconfigure(rows,weight=1)
        rows = rows + 1

    def update_variables(i):
        global variables
        variables[i] = sensativitySlider.get() #write the data currently in the fields
        variables[i+1] = lVolumeField.get()
        variables[i+2] = mVolumeField.get()
        variables[i+3] = hVolumeField.get() 
        variables[i+4] = vlPitchField.get()
        variables[i+5] = lPitchField.get()
        variables[i+6] = mPitchField.get()
        variables[i+7] = hPitchField.get()
        variables[i+8] = vhPitchField.get()

    def update_fields(i):
        global variables
        sensativitySlider.set(variables[i]) #put values in fields
        lVolumeField.delete(0, END)
        mVolumeField.delete(0, END)
        hVolumeField.delete(0, END)
        vlPitchField.delete(0, END)
        lPitchField.delete(0, END)
        mPitchField.delete(0, END)
        hPitchField.delete(0, END)
        vhPitchField.delete(0, END)
        lVolumeField.insert(END, str(variables[i+1]))
        mVolumeField.insert(END, str(variables[i+2]))
        hVolumeField.insert(END, str(variables[i+3]))
        vlPitchField.insert(END, str(variables[i+4]))
        lPitchField.insert(END, str(variables[i+5]))
        mPitchField.insert(END, str(variables[i+6]))
        hPitchField.insert(END, str(variables[i+7]))
        vhPitchField.insert(END, str(variables[i+8]))

    def start_logic():
        global stopLogic, lowVolume, midVolume, highVolume, lowPitch, midPitch, highPitch, speedLimit, calcmidPitch, veryhighPitch, verylowPitch, mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp, fpsKeysLogic, statusText, mouseLogic, fpsKeysLogic, sensativity, startButtonState, stopLogic, fpsLogic, X
        lowVolume, midVolume, highVolume = int(lVolumeField.get()), int(mVolumeField.get()), int(hVolumeField.get())
        lowPitch, midPitch, highPitch, veryhighPitch, verylowPitch, sensativity = int(lPitchField.get()), int(mPitchField.get()), int(hPitchField.get()), int(vhPitchField.get()), int(vlPitchField.get()), int(sensativitySlider.get())
        #mouseLogic, fpsKeysLogic, fpsKeysLogic = mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp
        #if startButtonState == 1: #if it is the start button
        #    if ((mouseLogic == True) and ((lowVolume < midVolume and midVolume < highVolume) and (midPitch < highPitch))):
        #        startButtonState = 0
        #        startButton.config(text="STOP", bg="#F08080")
        #        statusText.config(text="MOUSE VERSION is now RUNNING.")
        #        stopLogic = False
        #        Thread(target = logicImplementation).start()
        #    elif ((fpsKeysLogic == True) and ((lowVolume < highVolume) and (verylowPitch < lowPitch and lowPitch < midPitch and midPitch < highPitch and highPitch < veryhighPitch))):
        #        startButtonState = 0
        #        startButton.config(text="STOP", bg="#F08080")
        #        statusText.config(text="FPS VERSION is now RUNNING.")
        #        stopLogic = False
        #        Thread(target = logicImplementation).start()
        #    elif ((lowVolume < midVolume and midVolume < highVolume) and (verylowPitch < lowPitch and lowPitch < midPitch and midPitch < highPitch and highPitch < veryhighPitch)):
        #        startButtonState = 0
        #        startButton.config(text="STOP", bg="#F08080")
        #        statusText.config(text="FPS VERSION (KEYS ONLY) is now RUNNING.")
        #        stopLogic = False
        #        Thread(target = logicImplementation).start()
        #    else:
        #        statusText.config(text="*******Make sure inputs are integers and in order, then try again******")
        #else: #it is the stop button
        #    startButtonState = 1
        #    mouseLogic, fpsLogic, fpsKeysLogic = False, False, False
        #    stopLogic = True
        #    statusText.config(text="The program is now STOPPED")
        #    if mouseLogicTemp == True:
        #        startButton.config(text="START MOUSE", bg="#90EE90")
        #    elif fpsKeysLogicTemp == True:
        #        startButton.config(text="START FPS", bg="#90EE90")
        #    else:
        #        startButton.config(text="START FPS (KEYS)", bg="#90EE90")

        if ((mouseLogicTemp == True) and ((lowVolume < midVolume and midVolume < highVolume) and (midPitch < highPitch))): #Data Validation
            dataValidated = True
        elif ((fpsLogicTemp == True) and ((lowVolume < highVolume) and (verylowPitch < lowPitch and lowPitch < midPitch and midPitch < highPitch and highPitch < veryhighPitch))):
            dataValidated = True
        elif ((lowVolume < midVolume and midVolume < highVolume) and (verylowPitch < lowPitch and lowPitch < midPitch and midPitch < highPitch and highPitch < veryhighPitch)):
            dataValidated = True
        else:
            dataValidated = False

        if dataValidated == True:
            if mouseLogic == True: #if mouse is running when button pressed
                if mouseLogicTemp == True: #mouse tab is open
                    startButton.config(text="START MOUSE", bg="#90EE90")
                    statusText.config(text="The program is now STOPPED.")
                    mouseLogic, fpsLogic, fpsKeysLogic = False, False, False
                    stopLogic = True
                elif fpsLogicTemp == True: #fps tab is open
                    startButton.config(text="STOP", bg="#F08080")
                    statusText.config(text="FPS VERSION is now RUNNING.")
                    mouseLogic, fpsKeysLogic, fpsLogic = mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp
                else: #fps keys tab is open
                    startButton.config(text="STOP", bg="#F08080")
                    statusText.config(text="FPS (keys only) VERSION is now RUNNING.")
                    mouseLogic, fpsKeysLogic, fpsLogic = mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp

            elif fpsLogic == True: #if fps is running when button pressed
                if fpsLogicTemp == True: #fps tab is open
                    startButton.config(text="START FPS", bg="#90EE90")
                    statusText.config(text="The program is now STOPPED.")
                    mouseLogic, fpsLogic, fpsKeysLogic = False, False, False
                    stopLogic = True
                elif fpsKeysLogicTemp == True: #fps keys tab is open
                    startButton.config(text="STOP", bg="#F08080")
                    statusText.config(text="FPS (keys only) VERSION is now RUNNING.")
                    mouseLogic, fpsKeysLogic, fpsLogic = mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp
                else: #mouse tab is open
                    startButton.config(text="STOP", bg="#F08080")
                    statusText.config(text="MOUSE VERSION is now RUNNING.")
                    mouseLogic, fpsKeysLogic, fpsLogic = mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp

            elif fpsKeysLogic == True: #fps keys is running when button pressed
                if fpsKeysLogicTemp == True: #fps keys tab open
                    startButton.config(text="START FPS (KEYS)", bg="#90EE90")
                    statusText.config(text="The program is now STOPPED.")
                    mouseLogic, fpsLogic, fpsKeysLogic = False, False, False
                    stopLogic = True
                elif mouseLogicTemp == True: #mouse tab open
                    startButton.config(text="STOP", bg="#F08080")
                    statusText.config(text="MOUSE VERSION is now RUNNING.")
                    mouseLogic, fpsKeysLogic, fpsLogic = mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp
                else: #fps tab open
                    startButton.config(text="STOP", bg="#F08080")
                    statusText.config(text="FPS VERSION is now RUNNING.")
                    mouseLogic, fpsKeysLogic, fpsLogic = mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp

            else: #nothing is running
                if mouseLogicTemp == True:
                    mouseLogic, fpsKeysLogic, fpsLogic = mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp
                    startButton.config(text="STOP", bg="#F08080")
                    statusText.config(text="MOUSE VERSION is now RUNNING.")
                    stopLogic = False
                    Thread(target = logicImplementation).start()
                elif fpsLogicTemp == True:
                    mouseLogic, fpsKeysLogic, fpsLogic = mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp
                    startButton.config(text="STOP", bg="#F08080")
                    statusText.config(text="FPS VERSION is now RUNNING.")
                    stopLogic = False
                    Thread(target = logicImplementation).start()
                else:
                    mouseLogic, fpsKeysLogic, fpsLogic = mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp
                    startButton.config(text="STOP", bg="#F08080")
                    statusText.config(text="FPS VERSION (KEYS ONLY) is now RUNNING.")
                    stopLogic = False
                    Thread(target = logicImplementation).start()
        else:
            statusText.config(text="*******Make sure inputs are integers and in order, then try again******")

    def mouseButton():
        global mouseButton, fpsButton, keyOnlyButton, mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp, canvas, mouseDiagram, vlPitchField, vhPitchField, startButtonState, mouseLogic
        sensativitySlider.config(state=NORMAL)
        mVolumeField.config(state=NORMAL)
        if fpsLogicTemp == True: #if we came from "FPS GAME VERSION" button, save the values to those
            update_variables(9)
        elif fpsKeysLogicTemp == True:
            update_variables(18)
        update_fields(0)
        mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp = True, False, False
        fpsButton.config(bg="SystemButtonFace")
        mouseButton.config(bg="#daedf4")
        keyOnlyButton.config(bg="SystemButtonFace")
        if os.path.exists('Mouse Diagram.png'):
            canvas.create_image(0,0, anchor=NW, image=mouseDiagram)
        explanationText1.config(text="The Mouse Only version acts as a voice replacement for a mouse. ")
        explanationText2.config(text="This includes moving the cursor, L/R clicking, scrolling, and dragging.")
        explanationText3.config(text=" ")
        vhPitchField.config(state=DISABLED)
        vlPitchField.config(state=DISABLED)
        if mouseLogic == True: #if program is running in mouse mode
            startButton.config(text="STOP MOUSE", bg="#F08080")
        else:
            startButton.config(text="START MOUSE", bg="#90EE90")

    def fpsButton():
        global mouseButton, fpsButton, keyOnlyButton, mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp, fpsDiagram, canvas, vlPitchField, vhPitchField, startButtonState, fpsLogic
        vhPitchField.config(state=NORMAL)
        vlPitchField.config(state=NORMAL)
        sensativitySlider.config(state=NORMAL)
        mVolumeField.config(state=NORMAL)
        if mouseLogicTemp == True: #if we came from other buttons, save the values to those fields
            update_variables(0)
        elif fpsKeysLogicTemp == True:
            update_variables(18)
        update_fields(9)
        mouseLogicTemp, fpsLogicTemp, fpsKeysLogicTemp = False, True, False
        mouseButton.config(bg="SystemButtonFace")
        fpsButton.config(bg="#daf4e1")
        keyOnlyButton.config(bg="SystemButtonFace")
        if os.path.exists('FPS Diagram.png'):
            canvas.create_image(0,0, anchor=NW, image=fpsDiagram)
        explanationText1.config(text="The FPS Game version acts as a voice replacement for a mouse  ")
        explanationText2.config(text="and keyboard in the context of games. This includes moving the ")
        explanationText3.config(text="cursor, shooting, jumping, throwing grenades, etc.")
        if fpsLogic == True: #if program is running in fps mode
            startButton.config(text="STOP FPS", bg="#F08080")
        else:
            startButton.config(text="START FPS", bg="#90EE90")

    def keyOnlyButton():
        global mouseButton, fpsButton, keyOnlyButton, mouseLogicTemp, fpsKeysLogicTemp, fpsLogicTemp, canvas, fps_onlykey_Diagram, vlPitchField, vhPitchField, startButtonState, fpsKeysLogic
        vhPitchField.config(state=NORMAL)
        vlPitchField.config(state=NORMAL)
        if mouseLogicTemp == True: #if we came from other buttons, save the values to those fields
            update_variables(0)
        elif fpsLogicTemp == True:
            update_variables(9)
        update_fields(18)
        mouseLogicTemp, fpsLogicTemp, fpsKeysLogicTemp = False, False, True
        mouseButton.config(bg="SystemButtonFace")
        keyOnlyButton.config(bg="#f4dae0")
        fpsButton.config(bg="SystemButtonFace")
        if os.path.exists('FPS (key only) Diagram.png'):
            canvas.create_image(0,0, anchor=NW, image=fps_onlykey_Diagram)
        explanationText1.config(text="The FPS (keyboard only) version is the same as the FPS Game version, but minus any ")
        explanationText2.config(text="mouse movement. This version could be useful if you already have another way of using ")
        explanationText3.config(text="the mouse, for instance a head mouse.")
        mVolumeField.config(state=DISABLED)
        if fpsKeysLogic == True: #if program is running in fps key mode
            startButton.config(text="STOP FPS (KEYS)", bg="#F08080")
        else:
            startButton.config(text="START FPS (KEYS)", bg="#90EE90")
        sensativitySlider.config(state=DISABLED)

    def saveStatus_clear():
        saveStatus.config(text="")

    def restore_defaults():
        global variables, defaults
        variables = defaults
        if mouseLogicTemp == True: #if we came from "FPS GAME VERSION" button, save the values to those
            update_fields(0)
        elif fpsLogicTemp == True:
            update_fields(9)
        else:
            update_fields(18)
        
    def save_presets(): ##### FILE IO ########
        global variables
        if mouseLogicTemp == True:
            update_variables(0)
        elif fpsLogicTemp == True:
            update_variables(9)
        else:
            update_variables(18)
        with open('VoicePresets.txt', 'w+') as presets: #actually write variables[] to file
            for i in range(len(variables)):
                presets.write(str(variables[i]) + "\n")
        saveStatus.config(text="**** presets saved ****")
        saveStatus.after(3000, saveStatus_clear)

    ###### creating widgets #######
    lVolumeText = Label(root, text="Low Volume (silence): ") #creating text widgets
    mVolumeText = Label(root, text="Middle Volume: ")
    hVolumeText = Label(root, text="High Volume: ")
    vlPitchText = Label(root, text="Very Low Pitch: ")
    lPitchText = Label(root, text="Low Pitch: ")
    mPitchText = Label(root, text="Middle Pitch: ")
    hPitchText = Label(root, text="High Pitch: ")
    vhPitchText = Label(root, text="Very High Pitch: ")
    buttonText = Label(root, text="Choose your Version: ")
    sensativityText = Label(root, text="Sensativity: ")
    statusText = Label(root, text="The program is now STOPPED")
    explanationText1 = Label(root, text="The Mouse Only version acts as a voice replacement for a mouse. ")
    explanationText2 = Label(root, text="This includes moving the cursor, L/R clicking, scrolling, and dragging.")
    explanationText3 = Label(root, text=" ")
    pitchReadoutText = Label(root, text="Pitch: ",font=("Courier", 20))
    volumeReadoutText = Label(root, text="Volume: ",font=("Courier", 20))
    actionReadoutText = Label(root, text="Action: ",font=("Courier", 20))
    spaceFillerText = Label(root, text="                        ")
    saveStatus = Label(root, text=" ")

    mouseButton = Button(root, text="Mouse Only", padx=15, command=mouseButton, bg="#daedf4") #create a button/slider/text boxes
    fpsButton = Button(root, text="FPS Game Version", padx=15, command=fpsButton)
    keyOnlyButton = Button(root, text="FPS Keyboard Only", padx=15, command=keyOnlyButton)
    startButton = Button(root, text="START MOUSE", padx=50, pady=10, command=start_logic,bg="#90EE90")
    restore_defaults = Button(root, text="Restore Defaults", padx=15, command=restore_defaults)
    savePresetsButton = Button(root, text="Save Presets", padx=15, command=save_presets)
    sensativitySlider = Scale(root, from_=0, to=20, orient=HORIZONTAL)
    lVolumeField = Entry(root, width=7)
    mVolumeField = Entry(root, width=7) 
    hVolumeField = Entry(root, width=7) 
    vlPitchField = Entry(root, width=7) 
    lPitchField = Entry(root, width=7) 
    mPitchField = Entry(root, width=7) 
    hPitchField = Entry(root, width=7) 
    vhPitchField = Entry(root, width=7) 

    defaults = [6,4,60,200,115,135,260,600,700,  6,4,60,200,115,135,260,600,700,  6,4,60,200,130,160,260,500,650] #default values
    variables = [] #default values
    if os.path.exists('VoicePresets.txt'):
        with open('VoicePresets.txt', 'r') as presets:
            for line in presets:
                variables.append(int(line))
    else:
        variables = defaults

    sensativitySlider.set(variables[0]) #put default/preset values in fields upon program opening
    lVolumeField.insert(END, str(variables[1])) 
    mVolumeField.insert(END, str(variables[2]))
    hVolumeField.insert(END, str(variables[3])) 
    vlPitchField.insert(END, str(variables[4]))
    lPitchField.insert(END, str(variables[5]))
    mPitchField.insert(END, str(variables[6]))
    hPitchField.insert(END, str(variables[7]))
    vhPitchField.insert(END, str(variables[8]))
    

    vhPitchField.config(state=DISABLED)
    vlPitchField.config(state=DISABLED)
    
    canvas = Canvas(root, width=500, height=500)
    canvas.grid(row=24, column=0, columnspan=4, sticky=SW)
    if os.path.exists('Mouse Diagram.png'):
        mouseDiagram = PhotoImage(file="Mouse Diagram.png")
        canvas.create_image(0,0, anchor=NW, image=mouseDiagram)
    if os.path.exists('FPS Diagram.png'):
        fpsDiagram = PhotoImage(file="FPS Diagram.png")
    if os.path.exists('FPS (key only) Diagram.png'):
        fps_onlykey_Diagram = PhotoImage(file="FPS (key only) Diagram.png")

    ##### displaying widgets ########
    buttonText.grid(row=1,column=0) #display button stuff
    mouseButton.grid(row=1, column=1)
    fpsButton.grid(row=1, column=2)
    keyOnlyButton.grid(row=1,column=3)
    statusText.grid(row=23,column=0, columnspan=4, sticky=SW)
    explanationText1.grid(row=26,column=0, columnspan=4, sticky=SW)
    explanationText2.grid(row=27,column=0, columnspan=4, sticky=SW)
    explanationText3.grid(row=28,column=0, columnspan=4, sticky=SW)
    pitchReadoutText.grid(row=5,column=2, columnspan=3, rowspan=4, sticky=SW)
    volumeReadoutText.grid(row=9,column=2, columnspan=3, rowspan=4, sticky=SW)
    actionReadoutText.grid(row=13,column=2, columnspan=3, rowspan=4, sticky=SW)
    spaceFillerText.grid(row=0,column=4)
    saveStatus.grid(row=23,column=2)

    sensativityText.grid(row=3, column=0) #text widgets
    lVolumeText.grid(row=5, column=0) 
    mVolumeText.grid(row=7, column=0)
    hVolumeText.grid(row=9, column=0)
    vlPitchText.grid(row=11, column=0)
    lPitchText.grid(row=13, column=0)
    mPitchText.grid(row=15, column=0)
    hPitchText.grid(row=17, column=0)
    vhPitchText.grid(row=19, column=0)

    sensativitySlider.grid(row=3, column=1) #text field widgets
    lVolumeField.grid(row=5, column=1) 
    mVolumeField.grid(row=7, column=1)
    hVolumeField.grid(row=9, column=1)
    vlPitchField.grid(row=11, column=1)
    lPitchField.grid(row=13, column=1)
    mPitchField.grid(row=15, column=1)
    hPitchField.grid(row=17, column=1)
    vhPitchField.grid(row=19, column=1)
    startButton.grid(row=22, column=0, columnspan=2)
    savePresetsButton.grid(row=22, column=2)
    restore_defaults.grid(row=22, column=3)

    root.mainloop()



