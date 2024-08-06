import machine
from machine import Timer
twelve_hr_deleniation = "AM"
timestring = ""
is_twelve = False

hour24 = 0
minute = 0
second = 0
hour12 = 0

alarm_list = [0,0, ""]
alarm12_list =[0,0]
alarm24_list = [0,0]

sn24_alarm_list = [0,0]
sn12_alarm_list = [0,0]
snoozing = False
alarm_12hr_del = "AM"
snooze_duration = 1
alarm_active = False
alarm_now = False
alarm_hushed = False
sn_alarm_hushed = False


def snooze():
    global sn24_alarm_list, snoozing, snooze_duration, hour24, minute, is_twelve
    
    sn24_alarm_list = [hour24 ,minute + snooze_duration]
    
    if sn24_alarm_list[1] > 59 and (sn24_alarm_list[0] + 1) < 23:
        sn24_alarm_list[0] = sn24_alarm_list[0] + 1
        sn24_alarm_list[1] =  sn24_alarm_list[1] - 60
    elif sn24_alarm_list[1] > 59 and (sn24_alarm_list[0] + 1) > 23:
        sn24_alarm_list[0] = 0
        sn24_alarm_list[1] =  sn24_alarm_list[1] - 60   
            
            
    snoozing = True
    alarm_active = True
    print("Snooze list: ", sn24_alarm_list)
    
def set_alarm_active(req):
    global  alarm_active, snoozing
    if req == True and alarm_active == False:
        alarm_active = req
    elif req == False and alarm_active == True:
        alarm_active = req
        snoozing = False
        
def get_alarmtime_str():
    
    global alarm_list, is_twelve, alarm24_list, alarm12_list, alarm_12hr_del
    
    #print(len(alarm_list))
    
    if is_twelve == True:
        
        #print(alarm12_list)
        alarm_list = [alarm12_list[0],alarm12_list[1],alarm_12hr_del]
        """
        alarm_list[0] = alarm12_list[0]
        alarm_list[1] = alarm12_list[1]
        alarm_list[2] = alarm_12hr_del
        """
        
    else:
        
        alarm_list[0] = alarm24_list[0]
        alarm_list[1] = alarm24_list[1]
        alarm_list[2] = ""
        
        #print(alarm_list)
        
    return alarm_list

#edit_alarm_time      
def change_alarm_time(edit_alarm_list):
    
    global is_twelve, alarm24_list, alarm12_list, alarm_12hr_del
    
    if is_twelve == False:
        
        alarm24_list = edit_alarm_list
        alarm12_list[1] = edit_alarm_list[1]
        
        if alarm24_list[0] != 0 and alarm24_list[0] <= 12:
            
            alarm12_list[0] = alarm24_list[0]
            alarm_12hr_del = "AM"
        
        elif alarm24_list[0] > 12:
            
            alarm12_list[0] = alarm24_list[0] - 12
            alarm_12hr_del = "PM"
            
        else:
            
            alarm12_list[0] = 12
            alarm_12hr_del = "AM"
            
    else:
        
        alarm12_list = edit_alarm_list
        alarm24_list[1] = edit_alarm_list[1]
        
        if alarm_12hr_del == "AM" and alarm12_list[0] != 12:
            
            alarm24_list[0] = alarm12_list[0]
            
        elif alarm_12hr_del == "PM" and alarm12_list[0] != 12:
            
            alarm24_list[0] = alarm12_list[0] + 12
            
        elif alarm_12hr_del == "AM" and alarm12_list[0] == 12:
            
            alarm24_list[0] = 0
            
        else:
            
            alarm24_list[0] = 12
            
    
        
#set_alarm_12hr_del
def set_alarm_12hr_del(deleniation):
    
    global alarm24_list, alarm_12hr_del, is_twelve
    
    if is_twelve == True:
        
        """
        if deleniation == "AM" and alarm24_list[0] >= 12:
            alarm24_list[0] = alarm24_list[0] - 12
        elif deleniation == "PM" and alarm24_list[0]<12 :
            alarm24_list[0] = alarm24_list[0] + 12
        """
           
        alarm_12hr_del = deleniation
        
#change_alarm1224
def change_alarm1224(system):
    
    global alarm24_list, alarm_list, alarm_12hr_del, is_twelve, alarm12_list
    
    if system == "12": # 24 to 12
        
        """
        if alarm24_list[0] > 12:
            print("24 to 12, PM")
            alarm_list[0] = alarm24_list[0] - 12
            alarm_list[1] = alarm24_list[1]
            alarm_12hr_del = "PM"
        else:
            print("24 to 12, AM")
            
            if alarm24_list[0] == 0:
                alarm_list[0] = 12
            else:
                alarm_list[0] = alarm24_list[0]
        """
            
        alarm_list = [alarm12_list[0], alarm12_list[1], alarm_12hr_del]
        is_twelve = True
        #alarm_12hr_del = "AM"
        #print(f"Changing 24 to 12: 24list: {alarm24_list}, 12list: {alarm12_list}")    
    if system == "24": # 12 to 24
        
        """
        if alarm_12hr_del == "PM":
            alarm24_list[0] = alarm_list[0] + 12
            alarm24_list[1] = alarm_list[1]
        elif alarm_12hr_del == "AM":
            alarm24_list = alarm_list
        """
            
        alarm_list = [alarm24_list[0], alarm24_list[1], ""]
        #print(f"Changing 12 to 24: 24list: {alarm24_list}, 12list: {alarm12_list}") 
        is_twelve = False
            
def update_time(tim):
    global timestring,rtc,twelve_hr_deleniation, alarm_now, alarm_active,snoozing, sn24_alarm_list, alarm_hushed, sn_alarm_hushed, alarm24_list
    global hour24,minute,second,hour12
    timestamp=rtc.datetime()
    timestring24 = "%02d:%02d:%02d"%(timestamp[4:7])
    
    hour24 = timestamp[4]
    minute = timestamp[5]
    second = timestamp[6]
        
    if alarm_hushed == True and ([hour24, minute] != [alarm24_list[0], alarm24_list[1]]) and ([hour24, minute] != sn24_alarm_list) :
        alarm_hushed = False
    
    if sn_alarm_hushed == True and ([hour24, minute] != sn24_alarm_list):
        sn_alarm_hushed = False
    #print("Hour, minute", [hour24, minute])
    #print("Alarm24 time", alarm24_list)
    #print("Snooze time", sn24_alarm_list)
    
    if (([hour24, minute] == [alarm24_list[0], alarm24_list[1]]) and alarm_active == True and snoozing == False and alarm_hushed == False) or (sn_alarm_hushed == False and alarm_active == True and snoozing == True and ([hour24, minute] == sn24_alarm_list)):
        alarm_now = True
    else:
        alarm_now = False


    if is_twelve == True:

        if hour12 == 11 and minute == 59 and second == 59: # swap AM and PM
            print("swapping AM and PM")
            
            if twelve_hr_deleniation == "AM":
                twelve_hr_deleniation = "PM"
            else:
                twelve_hr_deleniation = "AM"
                
        if twelve_hr_deleniation == "PM" and hour24 >=13: 
            hour12 = hour24 - 12
        elif twelve_hr_deleniation == "AM" and hour24 == 0:
            hour12 = 12
        else:
            hour12 = hour24
        if hour12 == 13:
            hour12 = 1
        
        hr_str ="%02d:"%hour12
        timestring = hr_str + "%02d:%02d"%(timestamp[5:7])
    else:
        timestring = timestring24
    #print(f"alarm24_list: {alarm24_list}, 24hr time: [{hour24}, {minute}]")

def edit_time(edit_time_list):

    global twelve_hr_deleniation
    timestamp = rtc.datetime()
    """
    Taking an input from the display code 
    """
    hour = edit_time_list[0]
    minute = edit_time_list[1]
    second = edit_time_list[2]
    
    if hour == -1:
        hour = timestamp[4]
    if minute == -1:
        minute = timestamp[5]
    if second == -1:
        second = timestamp[6]
    if edit_time_list[0] == 12 and twelve_hr_deleniation =="AM":
        hour = 0
    #print(f"Changing 24hr time to: {hour} : {minute} : {second}")
    rtc.datetime((2023,7,30,2,hour,minute,second,0))
    
def rtc_set_1224(system):
    print("Toggling 12 / 24 hr")
    global hour24,minute,second,hour12,twelve_hr_deleniation, is_twelve
    if system == "12" and is_twelve == False :
    # going from 24 to 12
        print("Going from 24 to 12")   
        if hour24 > 12:
            twelve_hr_deleniation = "PM"
            hour12 = hour24 - 12
            
        elif hour24 == 12:
            twelve_hr_deleniation = "PM"
            hour12 = hour24
            
        elif hour24 == 0:
            hour12 = 12
            twelve_hr_deleniation = "AM"
            
        elif hour24 < 12:
            twelve_hr_deleniation = "AM"
            hour12 = hour24
            
        is_twelve = True
    elif system == "24" and is_twelve == True:
        #going from 12 to 24
        print("Going from 12 to 24") 
        if hour12 < 12 and twelve_hr_deleniation == "PM":
            hour24 = hour12 + 12
            
        elif hour12 == 12 and twelve_hr_deleniation == "AM":
            hour24 = 0
             # 12AM = 00:00
        elif hour12 == 12 and twelve_hr_deleniation == "PM":
            hour24 = 12
            
        elif hour12 < 12 and twelve_hr_deleniation == "AM":
            hour24 = hour12
            
        is_twelve = False   
    rtc.datetime((2023,7,30,2,hour24,minute,second,0))   
        
        
def rtc_setAMPM(deleniation):
    """
    Taking an input from the display code 
    """
    print("deleniation set to: " + deleniation )
    
    global is_twelve, twelve_hr_deleniation,rtc
    global hour24, minute, second

    if is_twelve == True:
        if deleniation == "AM" and hour24 > 12:
            #edit_time_list = [timestamp[4] - 12,timestamp[5],timestamp[6]]
            rtc.datetime((2023,7,30,2,hour24 - 12,minute,second,0))
            
        elif deleniation == "PM" and hour24 < 12:
            #edit_time_list = [timestamp[4] + 12,timestamp[5],timestamp[6]]
            rtc.datetime((2023,7,30,2,hour24 + 12,minute,second,0))
        elif deleniation == "PM" and hour24 == 12:
            hour24 = 12
            rtc.datetime((2023,7,30,2,hour24,minute,second,0))
        elif deleniation == "AM" and hour24 == 12:
            print("hour24 = 12" )
            hour24 = 0
            rtc.datetime((2023,7,30,2,hour24,minute,second,0))
            
    twelve_hr_deleniation = deleniation
    

def start_timing():
    global rtc
    global tim
    rtc = machine.RTC()
    rtc.datetime((2023, 7, 31, 2, 17, 48, 0, 0))
    tim = Timer(mode = Timer.PERIODIC, period = 1000, callback = update_time )
    
