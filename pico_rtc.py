import machine
from machine import Timer
timestring = ""
def print_time(tim):
    global timestring
    global rtc
    timestamp=rtc.datetime()
    timestring = "%02d:%02d:%02d"%(timestamp[4:7])
    #print("Pico time: ", str(timestring))
    

def start_timing():
    global rtc
    global tim
    rtc = machine.RTC()
    rtc.datetime((2023, 7, 31, 2, 17, 48, 0, 0))
    tim = Timer(mode = Timer.PERIODIC, period = 1000, callback = print_time )
    