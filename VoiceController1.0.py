import crepe
from scipy.io import wavfile
import time
import numpy as np
import win32api, win32con
import KeyPressing
import pyaudio
import wave
import audioop
from threading import Thread

global silence, seconds, fs, X1, X2, Low1, Low2, High1, High2, volume, pitch, midVolume, highVolume, verylowPitch, lowPitch, midPitch, highPitch, veryhighPitch

silence, X2, Low2, High2 = True, 0, 0, 0
midVolume, highVolume, midVol2 = int(130/2), 300, 130
verylowPitch, lowPitch, midPitch, highPitch, veryhighPitch = 115, 135, 230, 550, 700
calcMidPitch = int((lowPitch+highPitch)/2)

channels, chunk, fs, seconds = 1, int(1024/2), 16000, .06 #chunks per sample, sample rate, duration of each while loop recording
sample_format = pyaudio.paInt16  # 16 bits per sample
filename = "testfile.wav"

def logic():
    # Main Logic (only execute logic if noise is above a threshold), start by releasing all keys
    global X1, X2, Low1, Low2, Low3, High1, High2, High3, volume, pitch, midVolume, highVolume, verylowPitch, lowPitch, midPitch, highPitch, veryhighPitch, silence
    
    if (volume <= 2):
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
                KeyPressing.PressKey(0x10) #q
                time.sleep(0.1)
                KeyPressing.ReleaseKey(0x10)
                time.sleep(0.1)
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    
        # If Pitch is on lower side of "midpoint"
        elif pitch <= midPitch:
            Low1 = Low2
            Low2 = time.time()
            KeyPressing.ReleaseAll()
            if (Low2-Low1) > 0.20 and (Low2-Low1) < 0.6: # check for double low (difference between last timestamp you were low and this time)
                print("pressing G")
                KeyPressing.PressKey(0x22) #g
            elif pitch <= lowPitch and pitch > verylowPitch:
                print("Pressing E")
                KeyPressing.PressKey(0x12) #e
            elif pitch <= verylowPitch:
                KeyPressing.PressKey(0x13) #r
                print("Pressing R")
            else:
                print("MOVING MOUSE")
                if volume-midVolume < midVol2:
                    for i in range(5): #makes it move more the lower your pitch is
                        KeyPressing.MoveMouse(int(.05*(pitch-calcMidPitch)),int(.15*(midVolume-volume-10)))
                        time.sleep(.015)
                else:
                    for i in range(5): #makes it move more the lower your pitch is
                        KeyPressing.MoveMouse(int(.05*(pitch-calcMidPitch)),int(.15*(midVolume)))
                        time.sleep(.015)
                                   
        # If Pitch is on higher side of "midpoint"
        else:
            High1 = High2
            High2 = time.time()
            KeyPressing.ReleaseAll()
            if (High2-High1) > 0.2 and (High2-High1) < 0.6: #check for double high pitch
                print("Pressing SPACEBAR")
                KeyPressing.PressKey(0x39) #spacebar
            elif pitch > highPitch and pitch <= veryhighPitch:
                print("Pressing W")
                KeyPressing.PressKey(0x11) #w
            elif pitch > veryhighPitch:
                print("Pressing SHIFT + W")
                KeyPressing.PressKey(0x2a) #shift
                KeyPressing.PressKey(0x11) #w
            else:
                print("MOVING MOUSE")
                if volume-midVolume < midVol2:
                    for i in range(5): #makes it move more the lower your pitch is
                        KeyPressing.MoveMouse(int(.05*(pitch-calcMidPitch)),int(.15*(midVolume-volume-10)))
                        time.sleep(.015)
                else:
                    for i in range(5): #makes it move more the lower your pitch is
                        KeyPressing.MoveMouse(int(.05*(pitch-calcMidPitch)),int(.15*(midVol2)))
                        time.sleep(.015)

############################ MAIN ##############################
# Order of Importance of Actions:
# high volume >> low and high pitches >> everything else
################################################################WW

if __name__ == '__main__':
    while True:
        global volume, pitch

        if not(win32api.GetKeyState(0x4C) == 0 or win32api.GetKeyState(0x4C) == 1): #if L is pressed
            exit()

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
        sr, audio = wavfile.read(filename)
        time1, frequency, confidence, activation = crepe.predict(audio, fs, model_capacity="tiny", viterbi=False, step_size = int(seconds*1000))
        pitch = frequency[0] # measured in Hz
        if (volume > 2):
            print("pitch: ", pitch, "volume: ", volume, "|" * int(volume))
        Thread(target = logic).start()
        #logic()
        
