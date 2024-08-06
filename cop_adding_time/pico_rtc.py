import machine
from machine import Timer
twelve_hr_deleniation = "AM"
timestring = ""
is_twelve = False


def print_time(tim):
    global timestring
    global rtc
    global twelve_hr_deleniation
    timestamp=rtc.datetime()
    timestring24 = "%02d:%02d:%02d"%(timestamp[4:7])
    hour = timestamp[4]
    
    if is_twelve == True:
        if hour > 12:
            hour = hour - 12
        """
            #twelve_hr_deleniation = "PM"
        else:
            #twelve_hr_deleniation = "AM"
        """
        hr_str ="%02d:"%hour
        timestring = hr_str + "%02d:%02d"%(timestamp[5:7])
    else:
        timestring = timestring24
        twelve_hr_deleniation = ""
    #print("Pico time: ", str(timestring))
    
def edit_time(edit_time_list):

    global twelve_hr_deleniation
    timestamp = rtc.datetime()
    hour = edit_time_list[0]
    minute = edit_time_list[1]
    second = edit_time_list[2]
    
    if (is_twelve == True) and twelve_hr_deleniation == "PM":
        hour = hour + 12
    if hour == -1:
        hour = timestamp[4]
    if minute == -1:
        minute = timestamp[5]
    if second == -1:
        second = timestamp[6]
    rtc.datetime((2023,7,30,2,hour,minute,second,0))
    
    
            
def start_timing():
    global rtc
    global tim
    rtc = machine.RTC()
    rtc.datetime((2023, 7, 31, 2, 17, 48, 0, 0))
    tim = Timer(mode = Timer.PERIODIC, period = 1000, callback = print_time )
    