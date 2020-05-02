# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 15:06:02 2020
@author: Taufik Sutanto
"""
import os, sys, time
from tqdm import tqdm

# C:\Users\Username\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
def pyPriority():
    try:
        sys.getwindowsversion()
    except AttributeError:
        isWindows = False
    else:
        isWindows = True
    if isWindows:
        import win32api,win32process,win32con
        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
    else:
        os.nice(10)
        
if __name__ == '__main__':
    nHours = 6 * 3600
    pyPriority()
    print('I will restart the computer: ...')
    for i in tqdm(range(nHours)):
        time.sleep(1)
    
    print("Restarting the computer ... ")
    os.system("shutdown -t 0 -r -f")