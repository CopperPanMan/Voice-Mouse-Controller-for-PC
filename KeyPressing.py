import ctypes
import time
import win32api, win32con

SendInput = ctypes.windll.user32.SendInput

##################################################################################################
##### code by hodka and user573949 on stackoverflow  #############################################
### https://stackoverflow.com/questions/14489013/simulate-python-keypresses-for-controlling-a-game

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def MoveMouse(x, y):
    time.sleep(.005)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)

def ReleaseAll(): #releases all keys
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0) #left mouse

def ReleaseAll(): #specific to the hotkeys Halo Reach uses
    ReleaseKey(0x11) #w
    ReleaseKey(0x2a) #left shift
    ReleaseKey(0x12) #e
    ReleaseKey(0x13) #r (?)
    ReleaseKey(0x22) #g
    ReleaseKey(0x39) #spacebar
    ReleaseKey(0x10) #q
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

#Directx scan codes (what hexKeyCode to input): https://wiki.nexusmods.com/index.php/DirectX_Scancodes_And_How_To_Use_Them
#note - these are in decimal, you'll have to convert them to hex and then add a "0x" to the front