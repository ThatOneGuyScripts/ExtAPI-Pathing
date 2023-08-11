import sys
import time
import re

import pywintypes
import win32file
import win32pipe
import struct

defaultPipeName = "my_pipe"
def send_data_to_pipe(data):
    PIPENAME = defaultPipeName
    TIMEOUT = 0.1 # seconds
    attempts = 0
    while True:
        attempts += 1
        try:
            handle = win32file.CreateFile(
                fr"\\.\\pipe\{PIPENAME}",
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None,
            )
        except pywintypes.error:
            if attempts >= 10:
                print("Giving up, could not connect")
                sys.exit(2)
            print("Retrying...")
            time.sleep(1)
        else:
            break
    win32pipe.SetNamedPipeHandleState(
        handle,
        win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_NOWAIT,
        None,
        None,
    )
    data = data + "\n"
    win32file.WriteFile(handle, data.encode())
    start_time = time.monotonic()
    result = ""
    data = b""

    while True:
        try:
            status, chunk = win32file.ReadFile(handle, 32768)
            data += chunk
            if len(chunk) < 32768:
                break
        except pywintypes.error as e:
            error_code = e.args[0]
            if error_code == 232: # ERROR_NO_DATA
                if time.monotonic() - start_time > TIMEOUT:
                    print("Timeout while waiting for result")
                    break
                time.sleep(0.1)
            else:
                print(f"Error {error_code} while trying to read from pipe")
                break
    result =data.decode()
    win32file.CloseHandle(handle)
    return result


def setShortestPathTarget(x,y,z):
    data = send_data_to_pipe(f"setShortestPathTarget {x} {y} {z}")
    

    

#data = getInventorySlotsContainingItem(0)
#print(data)              
#data = getEquippedWeapon()
#print(data)