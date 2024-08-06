from machine import SPI,Pin, Timer, ADC
import utime

# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
#from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class NOT IN USE
import framebuf # this is another library for the display.
import button_interrupt
import sn_button_interrupt
from xglcd_font import XglcdFont
from ssd1309 import Display
import pico_rtc
import Cursor
import encoder2
from radio import Radio
import lightsensor
import beeper

class Menu:
    def __init__(self,name, options, drawing_function):
        self.name = name
        self.options = options
        self.drawing_function = drawing_function
        
class screen:
    """
    ->Main Menu (Shows time, Last Set Radio Station,next timer, volume adjustment)
    (Becomes active when timer runs out or when "go back to main menu is selected" from the settings menu
        Displays:
            - Time
            - Last Set Radio Station
            - Next set timer
            - Volume Slider
    ->Settings Menu
        (Becomes Active when UI button pushed)
        Shows options to:
            - Go back to main menu
            - Go to Alarm settings menu
            - Go to set Current time and date
            - Got to brightness adjustment method
            
    -> Alarm Set menu
    -> Brightness adjustment Menu
    -> Current time and date menu
    -> 
    
    
    """

    
    def __init__(self):
        self.mainMenuOptions = {
            "Frequency" : [6, self.change_frequency],
            "Alarms": [2, self.goto_alarm_settings_menu],
            "MUTE": [3, self.mute_volume],
            "Vol": [4,self.goto_volume_menu],
            "Time": [5, self.goto_clock_menu],
            "Brightness": [1, self.goto_brightness_menu]
 
            }
        
        
        self.MainMenu = Menu("Main Menu", self.mainMenuOptions, self.drawMainMenu)
        
        self.volumeMenuOptions = {
            "Go to main menu" : [self.MainMenu.options["Vol"][0], self.goto_main_menu] #one option: go back 
            }
        
        self.frequencyMenuOptions = {
            "Go to main menu" : [self.MainMenu.options["Frequency"][0], self.goto_main_menu]
            }
        
        self.brightnessMenuOptions = {
            "Back" : [0, self.goto_main_menu],
            "Manual" : [1, self.goto_manual_mode],
            "Change when dark" : [2, self.goto_lightsensor_menu],
            }
        
        self.minimalModeOptions = {
            "Back" : [0, self.goto_main_menu_fr_minimal_mode]
            }
        
        self.AlarmSettingsMenuOptions = {
            "Back" : [0, self.goto_main_menu_fr_alarm_menu],
            "Alarm Hour" : [1, self.goto_alarm_hour_menu],
            "Alarm Minute": [2,self.goto_alarm_minute_menu],
            "Repeat alarm?" : [3, self.toggle_repeat_alarm],
            "Snooze Duration":[4, self.goto_set_snooze_menu],
            "Beeper or Radio" : [5, self.toggle_beeper_or_radio],
            "Toggle Alarm" : [6,self.toggle_alarm],
            "AM/PM" : [7,self.toggle_alarm_AMPM]
            
            }
        self.alarmMinuteMenuOptions = {
            "Back": [self.AlarmSettingsMenuOptions["Alarm Minute"][0], self.goto_alarm_settings_menu]
        }
        self.alarmHourMenuOptions = {
            "Back": [self.AlarmSettingsMenuOptions["Alarm Hour"][0], self.goto_alarm_settings_menu]
        }
        self.clockMenuOptions = {
            "Back" : [0, self.goto_main_menu],
            "Change hour" : [1, self.goto_hour_menu],
            "Change minute" : [2, self.goto_minute_menu],
            "Change second" : [3, self.goto_second_menu],
            "12/24hr":[4,self.toggle1224hr],
            "AM/PM":[5,self.toggleAMPM],
            "Save":[6, self.save_time_edit]
            }
        
        self.hourMenuOptions ={
            "Back" : [self.clockMenuOptions["Change hour"][0], self.goto_clock_menu]
            }
        
        self.minuteMenuOptions = {
            "Back" : [self.clockMenuOptions["Change minute"][0],self.goto_clock_menu]
            }
        
        self.secondMenuOption = {
            "Back" : [self.clockMenuOptions["Change second"][0], self.goto_clock_menu]
            }
        self.setSnoozeMenuOptions = {
            "Back" : [self.AlarmSettingsMenuOptions["Snooze Duration"][0], self.goto_alarm_settings_menu]
            }
        self.alarmMenuOptions = {
            "Back and stop alarm" : [0, self.goto_main_menu_stop_alarm]
            }
        self.AlarmMenu = Menu("Alarm menu", self.alarmMenuOptions,self.drawAlarmMenu)
        self.SetSnoozeMenu = Menu("Set Snooze Menu", self.setSnoozeMenuOptions,self.drawSnoozeMenu)
        self.AlarmHourMenu = Menu("Alarm Hour Menu", self.alarmHourMenuOptions,self.drawAlarmHourMenu)
        self.AlarmMinuteMenu = Menu("Alarm Minute Menu", self.alarmMinuteMenuOptions, self.drawAlarmMinuteMenu)
        self.AlarmSettingsMenu = Menu("Alarm Menu", self.AlarmSettingsMenuOptions,self.drawAlarmSettingsMenu)
        self.HourMenu = Menu("Hour Menu", self.hourMenuOptions,self.drawHourMenu)
        self.MinuteMenu = Menu("Minute Menu", self.minuteMenuOptions, self.drawMinuteMenu)
        self.SecondMenu = Menu ("Second Menu", self.secondMenuOption,self.drawSecondMenu)
        self.ClockMenu = Menu("Clock menu", self.clockMenuOptions, self.drawClockMenu)
        self.VolumeMenu = Menu("Volume Menu", self.volumeMenuOptions, self.drawVolumeMenu)
        self.FrequencyMenu = Menu("Frequency Menu", self.frequencyMenuOptions, self.drawFrequencyMenu)
        self.BrightnessMenu = Menu("Brightness Menu", self.brightnessMenuOptions, self.drawBrightnessOptionsMenu)
        self.MinimalMode = Menu("Minimal Mode", self.minimalModeOptions, self.drawMinimalMode)
        
        #change the below map
        self.menuOptions = {
            "Main Menu" : self.MainMenu,
            "Volume Menu": (2, 5, self.drawVolumeMenu)}
        
        self.current_menu = self.menuOptions["Main Menu"]
        
        """
            Below goes the global settings
        """
        
        self.volume = 1
        self.current_frequency = 101.9
        self.current_next_alarm = "06:30"
        self.vol_percent = self.volume/15
        self.twelve_hr_deleniation = "AM"
        self.thd_to_edit = "AM"
        self.fm_radio = Radio(101.9, 1, True) #initializing radio
        self.fm_radio.SetFrequency(101.8)
        utime.sleep_ms(300)
        self.fm_radio.SetFrequency(101.9)
        self.mutex = 0 #used to track if the radio should be muted or unmuted
        self.using_lightsensor = False
        self.using_manual_mode = False
        self.edit_time_list = [-1,-1,-1]
        pico_rtc.start_timing()
        
        
        self.edit_alarm_list = [0,0]
        self.snooze_duration = 1
        self.alarm_string = "--:--"
        self.alarm_12hr_del = "AM"
        self.alarm_active = False
        self.repeat_alarm = False
        self.beeper_or_radio = "beeper"
        
    def goto_main_menu(self):
        
        #dont forget to make sure you are using the normal cursor
        Cursor.using_sp = False
        #Cursor.cursor_value = 1
        self.current_menu = self.MainMenu
        
    def goto_alarm_menu(self):
        
        Cursor.using_sp = True
        Cursor.cursor_value = 0
        
        if self.beeper_or_radio == "radio":
            self.fm_radio.SetMute(False)
        else:
            beeper.sound_beeper()      
            self.fm_radio.SetMute(True)
        
        self.current_menu = self.AlarmMenu
        

            
    def goto_main_menu_fr_alarm_menu(self):
        
        pico_rtc.change_alarm_time(self.edit_alarm_list)
        
        self.goto_main_menu()
        
    def goto_main_menu_snooze(self):
        
        pico_rtc.sn_alarm_hushed = True
        pico_rtc.alarm_now = False
        
        if self.beeper_or_radio == "radio" and self.mutex%2 == 0 :
            self.fm_radio.SetMute(True)
        else:
            
            beeper.stop_beeper()
            
            """
            if self.mutex%2 != 0:
                
                self.fm_radio.setmute(False)
            """
            
        pico_rtc.snooze()
        self.goto_main_menu()
        
    def goto_main_menu_stop_alarm(self):
        
        #pico_rtc.set_alarm_active(False)
        pico_rtc.snooze_number = 1
        pico_rtc.snoozing = False
        pico_rtc.alarm_hushed = True
        pico_rtc.alarm_now = False
        
        if self.beeper_or_radio == "radio" and self.mutex%2 == 0:
            self.fm_radio.SetMute(True)
        else:
            beeper.stop_beeper()
        
        self.goto_main_menu()
        
    def goto_alarm_settings_menu(self):
        Cursor.using_sp = False
        Cursor.cursor_value = 0
        Cursor.Total_Numof_settings = len(self.AlarmSettingsMenu.options) - 1
        self.current_menu = self.AlarmSettingsMenu
        print("Going to Alarm Menu")
        
    def goto_alarm_hour_menu(self):
        Cursor.cursor_value = self.AlarmSettingsMenu.options["Alarm Hour"][0]
        Cursor.using_sp = True
        if pico_rtc.is_twelve == False:
            Cursor.max_sp_value = 23
            Cursor.sp_cursor_value = 0
        else:
            Cursor.max_sp_value = 11
            Cursor.sp_cursor_value = 0
        self.current_menu = self.AlarmHourMenu
        print("Going to alarm hour menu")
        
    def goto_set_snooze_menu(self):
        
        Cursor.cursor_value = self.AlarmSettingsMenu.options["Snooze Duration"][0]
        Cursor.using_sp = True
        Cursor.max_sp_value = 59
        Cursor.sp_cursor_value = 0
        self.current_menu = self.SetSnoozeMenu        
        print("Going to set snooze menu")
        
    def goto_alarm_minute_menu(self):
        Cursor.cursor_value = self.AlarmSettingsMenu.options["Alarm Minute"][0]
        Cursor.using_sp = True
        Cursor.max_sp_value = 59
        Cursor.sp_cursor_value = 0
        self.current_menu = self.AlarmMinuteMenu
        print("Going to new alarm minute menu")
        
    def toggle_alarm(self):
        print("Toggling alarm")
        if pico_rtc.alarm_active == False:
            pico_rtc.set_alarm_active(True)
        else:
            pico_rtc.set_alarm_active(False)
            
    def toggle_repeat_alarm(self):
        print("Toggling repeat alarm")
        if self.repeat_alarm == False:
            self.repeat_alarm = True
            

    def toggle_beeper_or_radio(self):
        
        print("Toggling beeper or radio")
        
        if self.beeper_or_radio == "beeper":
            self.beeper_or_radio = "radio"
            
        else:
            self.beeper_or_radio = "beeper"
            
        print(self.beeper_or_radio)
            
    def toggle_alarm_AMPM(self):
        if pico_rtc.alarm_12hr_del == "AM":
           pico_rtc.set_alarm_12hr_del("PM")
        else:
            pico_rtc.set_alarm_12hr_del("AM")
            
    def goto_clock_menu(self):
        Cursor.using_sp = False
        Cursor.cursor_value = 0
        Cursor.Total_Numof_settings = len(self.ClockMenu.options)
        self.current_menu = self.ClockMenu
        print("Going to clock menu")
      
    def goto_main_menu_fr_minimal_mode(self):
        self.display_1309.write_cmd(self.display_1309.CONTRAST_CONTROL)
        self.display_1309.write_cmd(0xFF)
        self.using_lightsensor = False
        self.using_manual_mode = False
        self.goto_main_menu()
    
    def goto_brightness_menu(self):
        
        Cursor.using_sp = False
        self.current_menu = self.BrightnessMenu
        Cursor.Total_Numof_settings = len(self.BrightnessMenu.options)
    
        print("going to brightness menu")
        
    def goto_lightsensor_menu(self):
        
        if self.using_lightsensor == True:
            self.using_lightsensor = False
        else:
            self.using_lightsensor = True
            
        self.using_manual_mode = False
        
        print("Using Light sensor")
        
    def goto_manual_mode(self):
        
        self.using_lightsensor = False
        self.using_manual_mode = True
        self.goto_main_menu()
        
        print("Using Manual Mode")
        
    def goto_minimal_mode(self):
        
        Cursor.using_sp = True
        Cursor.max_sp_value = 0
        Cursor.cursor_value = 0
        self.display_1309.write_cmd(self.display_1309.CONTRAST_CONTROL)
        self.display_1309.write_cmd(0x01)
        self.current_menu = self.MinimalMode
        
        print("Minimal mode")
        
    def goto_clock_menu(self):
        Cursor.using_sp = False
        Cursor.cursor_value = 0
        Cursor.Total_Numof_settings = len(self.ClockMenu.options)
        self.current_menu = self.ClockMenu
        print("Going to clock menu")
        
    def toggleAMPM(self):
        if pico_rtc.twelve_hr_deleniation == "AM":
            pico_rtc.rtc_setAMPM("PM")
        else:
            pico_rtc.rtc_setAMPM("AM")
            
        
    def goto_hour_menu(self):
        print("Going to hour menu")
        Cursor.cursor_value = self.ClockMenu.options["Change hour"][0]
        Cursor.using_sp = True
        if pico_rtc.is_twelve == False:
            Cursor.max_sp_value = 23
            Cursor.sp_cursor_value = 0
        else:
            Cursor.max_sp_value = 11
            Cursor.sp_cursor_value = 0
        self.current_menu = self.HourMenu
        
        
    def goto_minute_menu(self):
        print("Going to minute menu")
        Cursor.cursor_value = self.ClockMenu.options["Change minute"][0]
        Cursor.using_sp = True
        Cursor.max_sp_value = 59
        Cursor.sp_cursor_value = 0
        self.current_menu = self.MinuteMenu
        
    def goto_second_menu(self):
        Cursor.cursor_value = self.ClockMenu.options["Change second"][0]
        Cursor.using_sp = True
        Cursor.max_sp_value = 59
        Cursor.sp_cursor_value = 0
        self.current_menu = self.SecondMenu
        print("Going to second menu")

    def toggle1224hr(self):
        print("toggle1224hr")
        if pico_rtc.is_twelve == True:
            pico_rtc.rtc_set_1224("24")
            pico_rtc.change_alarm1224("24")
            self.edit_alarm_list = pico_rtc.get_alarmtime_str()
            # going from 12 to 24
            #self.edit_time_list[0] = pico_rtc.hour24

        else:        
            pico_rtc.rtc_set_1224("12")
            pico_rtc.change_alarm1224("12")
            self.edit_alarm_list = pico_rtc.get_alarmtime_str()
            #self.edit_time_list[0] = pico_rtc.hour12
            # going from 24 to 12
        
            
        if self.edit_time_list[0] != -1:
            print("changing edit_time_list[0]")
            
            if pico_rtc.is_twelve == False:
                print("is_twelve")
                #going from 12 to 24
                if pico_rtc.twelve_hr_deleniation == "AM" and self.edit_time_list[0] != 12:
                    pass # do nothing since 05:00 = 5AM
                    print("05:00 = 5AM")
                elif pico_rtc.twelve_hr_deleniation == "AM" and self.edit_time_list[0] == 12:
                    self.edit_time_list[0] = 0 # 12AM == 00:00
                    print("12AM == 00:00")
                elif pico_rtc.twelve_hr_deleniation == "PM" and self.edit_time_list[0] != 12:
                    self.edit_time_list[0] = self.edit_time_list[0] + 12 # 3PM = 15:00
                    print("3PM = 15:00")
                elif pico_rtc.twelve_hr_deleniation == "PM" and self.edit_time_list[0] == 12:
                    self.edit_time_list[0] = 12 # 12PM = 12:00
                    print("12PM = 12:00")
            else:
                #going from 24 to 12
                if 1 <= self.edit_time_list[0] <= 12:
                    pico_rtc.rtc_setAMPM("AM") # do nothing since 05:00 = 5AM and 12:00 = 12PM
                elif self.edit_time_list[0] == 0:
                    self.edit_time_list[0] = 12 #00:00 = 12AM
                    pico_rtc.rtc_setAMPM("AM")
                elif self.edit_time_list[0] > 12:
                    self.edit_time_list[0] = self.edit_time_list[0] - 12
                    pico_rtc.rtc_setAMPM("PM")
        
        
    def mute_volume(self):
        
        self.mutex = self.mutex + 1
        
        if self.mutex % 2 == 0:
            self.fm_radio.SetMute(True)
        else:
            self.fm_radio.SetMute(False)
          
        print("muting volume")
        
    def save_time_edit(self):
        pico_rtc.edit_time(self.edit_time_list)
        self.edit_time_list = [-1,-1,-1]
        #pico_rtc.twelve_hr_deleniation = self.thd_to_edit
        self.goto_main_menu()
        print("Saving Time")
        
    def goto_volume_menu(self):
        
        Cursor.cursor_value = self.MainMenu.options["Vol"][0]
        Cursor.using_sp = True
        Cursor.max_sp_value = 15
        self.current_menu = self.VolumeMenu
        Cursor.sp_cursor_value = self.volume
        print("changing volume")
        
    def change_frequency(self):
        
        Cursor.using_sp = True
        Cursor.max_sp_value = 200
        Cursor.sp_cursor_value = int((self.current_frequency - 88)*10)
        self.current_menu = self.FrequencyMenu
    
        print("changing frequency")
        
    def initDisplay1309(self):
        
            """
            Initialize spi pins (using spi 0)
            """
            spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
            spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
            spi_res = Pin(16) # res stands for reset; to be connected to a free GPIO pin
            spi_dc  = Pin(17) # dc stands for data/command; to be connected to a free GPIO pin
            spi_cs  = Pin(20) # chip select; to be connected to the SPI chip select of the Pico 
    
            spi = SPI(0, baudrate=10000000, sck=spi_sck, mosi=spi_sda)
            self.display_1309 = Display(spi, dc=spi_dc, cs=spi_cs, rst=spi_res)
            
            self.load_fonts()
            print("1309 Screen Initialized")
            
            
    def load_fonts(self):
        print("Loading unispace font")
        self.clockDisplay_Font = XglcdFont('fonts/Unispace12x24.c', 12, 24)
        print("Unispace font loaded")
        
        self.clockDisplay_width = self.clockDisplay_Font.measure_text("Unispace")
        self.clockDisplay_height = self.clockDisplay_Font.height
        
        print("Loading Main control Font")
        self.frequency_font = XglcdFont('fonts/ArcadePix9x11.c', 9, 11)
        #self.mainControls_Font = XglcdFont('fonts/Bally5x8.c', 5, 8)
        self.mainControls_Font = XglcdFont('fonts/Wendy7x8.c', 7, 8)
        print("Main Controls Font loaded")
    """  
    def initDisplay(self):
        print("Init display")
        pico_rtc.start_timing()
        # Define columns and rows of the oled display. These numbers are the standard values. 
        SCREEN_WIDTH = 128 #number of columns
        SCREEN_HEIGHT = 64 #number of rows

        # Initialize I/O pins associated with the oled display SPI interface
        spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
        spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
        spi_res = Pin(16) # res stands for reset; to be connected to a free GPIO pin
        spi_dc  = Pin(17) # dc stands for data/command; to be connected to a free GPIO pin
        spi_cs  = Pin(20) # chip select; to be connected to the SPI chip select of the Pico 

        #
        # SPI Device ID can be 0 or 1. It must match the wiring. 
        #
        SPI_DEVICE = 0 # Because the peripheral is connected to SPI 0 hardware lines of the Pico

        # initialize the SPI interface for the OLED display
        #
        self.oled_spi = SPI( SPI_DEVICE, baudrate= 100000, sck= spi_sck, mosi= spi_sda )

        #
        # Initialize the display
        #
        self.oled = SSD1306_SPI( SCREEN_WIDTH, SCREEN_HEIGHT, self.oled_spi, spi_dc, spi_res, spi_cs, True)
        self.oled.contrast(0x05)
     """   
    def updateDisplay1309(self):
        #
        # Clear the buffer
        #
        
        self.display_1309.clear_buffers()
        
        #
        # Update the text on the screen
        #
        
        self.current_menu.drawing_function()
        #self.drawMainMenu()
        
        #
        # Transfer the buffer to the oled screen
        #
        self.display_1309.present()
        
    def drawAlarmMenu(self):
        
        if sn_button_interrupt.Button_Active == True:
            sn_button_interrupt.Button_Active = False
            self.goto_main_menu_snooze()
            
        
        message_str = "WAKE UP"
        
        font = self.clockDisplay_Font
        
        x_val = 64 - int(font.measure_text(message_str)/2)
        y_val = 10
        
        self.display_1309.draw_text(x_val,y_val, message_str, font, invert = False)
        
        y_val = y_val + font.height
        x_val = 64 - int(font.measure_text(pico_rtc.timestring)/2)
        self.display_1309.draw_text(x_val, y_val, pico_rtc.timestring, font, invert = False)
    #drawAlarmMinuteMenu  
    def drawAlarmMinuteMenu(self):
        
        if self.edit_alarm_list[1] != Cursor.sp_cursor_value:
            self.edit_alarm_list[1] = Cursor.sp_cursor_value
            
            print("self.edit_alarm_list[1]", self.edit_alarm_list[1] )
            
        minute_str = str(self.edit_alarm_list[1])
        x_val = 5
        y_val = 32 - int(self.clockDisplay_Font.height/2)
        self.display_1309.draw_text(x_val,y_val,minute_str,self.clockDisplay_Font, invert = False)
    #drawAlarmHourMenu
    def drawAlarmHourMenu(self):
        
        if pico_rtc.is_twelve == True:
            if self.edit_alarm_list[0] != Cursor.sp_cursor_value + 1:
                self.edit_alarm_list[0] = Cursor.sp_cursor_value + 1
                
                """
                if pico_rtc.alarm_12hr_del == "PM":
                    self.edit_alarm_list[0] = self.edit_alarm_list[0] + 12
                    
                else: 
                    self.edit_alarm_list[0] = self.edit_alarm_list[0]
                """
                
                
        else:
            if self.edit_alarm_list[0] != Cursor.sp_cursor_value:
                self.edit_alarm_list[0] = Cursor.sp_cursor_value
                      
        hour_str = str(self.edit_alarm_list[0])
        #print("in alarm hour menu: edit_alarm_list[0]: ", self.edit_alarm_list[0])
        x_val = 5
        y_val = 32 - int(self.clockDisplay_Font.height/2)
        self.display_1309.draw_text(x_val,y_val,hour_str,self.clockDisplay_Font, invert = False)
            
    def drawMinuteMenu(self):
        if self.edit_time_list[1] != Cursor.sp_cursor_value:
            self.edit_time_list[1] = Cursor.sp_cursor_value
        minute_str = str(self.edit_time_list[1])
        x_val = 5
        y_val = 32 - int(self.clockDisplay_Font.height/2)
        self.display_1309.draw_text(x_val,y_val,minute_str,self.clockDisplay_Font, invert = False)
        
    def drawSecondMenu(self):
        if self.edit_time_list[2] != Cursor.sp_cursor_value:
            self.edit_time_list[2] = Cursor.sp_cursor_value
        second_str = str(self.edit_time_list[2])
        x_val = 5
        y_val = 32 - int(self.clockDisplay_Font.height/2)
        self.display_1309.draw_text(x_val,y_val,second_str,self.clockDisplay_Font, invert = False)
        
    def drawHourMenu(self):
        if pico_rtc.is_twelve == True:
            if self.edit_time_list[0] != Cursor.sp_cursor_value + 1:
                self.edit_time_list[0] = Cursor.sp_cursor_value + 1
            hour_str = str(self.edit_time_list[0])
            x_val = 5
            y_val = 32 - int(self.clockDisplay_Font.height/2)
            self.display_1309.draw_text(x_val,y_val,hour_str,self.clockDisplay_Font, invert = False)
        else:
            if self.edit_time_list[0] != Cursor.sp_cursor_value:
                self.edit_time_list[0] = Cursor.sp_cursor_value
            hour_str = str(self.edit_time_list[0])
            x_val = 5
            y_val = 32 - int(self.clockDisplay_Font.height/2)
            self.display_1309.draw_text(x_val,y_val,hour_str,self.clockDisplay_Font, invert = False)
    def drawSnoozeMenu(self):
        if pico_rtc.snooze_duration != Cursor.sp_cursor_value:
            pico_rtc.snooze_duration = Cursor.sp_cursor_value
            pico_rtc.snooze_duration = Cursor.sp_cursor_value
            print("snooze_duration", pico_rtc.snooze_duration )
        minute_str = str(pico_rtc.snooze_duration)
        x_val = 5
        y_val = 32 - int(self.clockDisplay_Font.height/2)
        self.display_1309.draw_text(x_val,y_val,minute_str,self.clockDisplay_Font, invert = False)
    #drawAlarmSettingsMenu
    def drawAlarmSettingsMenu(self):
        alarm_options = ["Back", "Alarm Hour","Alarm Minute", "Repeat alarm?", "Snooze Duration", "Beeper or Radio"]
        
        y_val = 0
        x_val = 5
        y_padding = 2
        dy = self.mainControls_Font.height + y_padding
        
        for option in alarm_options:
            if Cursor.cursor_value == self.AlarmSettingsMenu.options[option][0]:
                self.display_1309.draw_text(x_val,y_val,option,self.mainControls_Font, invert = True)
            else:
                self.display_1309.draw_text(x_val,y_val,option,self.mainControls_Font, invert = False)
            y_val = y_val + dy
        
        #drawing line under beeper or radio
        
        
        line_y_val = y_val + self.mainControls_Font.height + 1 - dy
        
        
        x_1 = x_val + self.mainControls_Font.measure_text("Beeper or ")
        x_2 = x_1 + self.mainControls_Font.measure_text("Radio") - 1
        x_3 = x_val
        x_4 = x_val + self.mainControls_Font.measure_text("Beeper")
        """
        print(x_1)
        print(x_2)
        print(x_3)
        print(x_4)
        print(line_y_val)
        """
        
        if self.beeper_or_radio == "radio":
        
            self.display_1309.draw_line(x_1, line_y_val, x_2, line_y_val, invert = False)
                
        else:

            self.display_1309.draw_line(x_3, line_y_val, x_4, line_y_val, invert = False)
               
        
        x_val = 70
        y_val = y_val-dy
        if Cursor.cursor_value == self.AlarmSettingsMenu.options["Toggle Alarm"][0]:
            self.display_1309.draw_text(x_val,y_val,"Toggle Alarm",self.mainControls_Font, invert = True)
        else:
            self.display_1309.draw_text(x_val,y_val,"Toggle Alarm",self.mainControls_Font, invert = False)
        y_val = y_val-dy
        
        sn_str = str(pico_rtc.snooze_duration)
        if len(sn_str) == 1:
            sn_str = "0" + sn_str
        self.display_1309.draw_text(x_val,y_val, "-> " + sn_str ,self.mainControls_Font, invert = False)
        
        x_val = x_val + 25
        
        if Cursor.cursor_value == self.AlarmSettingsMenu.options["AM/PM"][0]:
            self.display_1309.draw_text(x_val,y_val,"AM/PM",self.mainControls_Font, invert = True)
        else:
            self.display_1309.draw_text(x_val,y_val,"AM/PM",self.mainControls_Font, invert = False)
        
        
        y_val = y_val + int(self.mainControls_Font.height/2)
        if pico_rtc.is_twelve == False:
            self.display_1309.draw_line(x_val-1, y_val, x_val + self.mainControls_Font.measure_text("AM/PM"), y_val, invert = False)
           
        
        x_val = 70
        y_val = 0
        
        #drawing edit
        hour = "-"
        minute = "-"
        
        if self.edit_alarm_list[0] != -1:
            hour = str(self.edit_alarm_list[0])
            if self.edit_alarm_list[0] < 10:
                hour = "0" + hour
        if self.edit_alarm_list[1] != -1:
            minute = str(self.edit_alarm_list[1])
            if self.edit_alarm_list[1] < 10:
                minute = "0" + minute
            
                
            
        string = hour + " : " + minute 
        self.display_1309.draw_text(x_val,y_val,string, self.mainControls_Font, invert = False)
        
        y_val = y_val + int(self.mainControls_Font.height/2)
        
        if pico_rtc.alarm_active == False:
            dx = self.mainControls_Font.measure_text(string)
            self.display_1309.draw_line(x_val - 2, y_val, x_val + dx + 2, y_val, invert = False)
        
        y_val = y_val + int(self.mainControls_Font.height/2) 
        y_val = y_val + self.mainControls_Font.height + y_padding
        
        if pico_rtc.is_twelve == True:
            self.display_1309.draw_text(x_val,y_val,"(12)", self.mainControls_Font, invert = False)
        else:
            self.display_1309.draw_text(x_val,y_val,"(24)", self.mainControls_Font, invert = False)
        
        x_val = x_val + self.mainControls_Font.measure_text("(24)")
                
        if pico_rtc.is_twelve == False:
            self.display_1309.draw_text(x_val + 2,y_val,"("+pico_rtc.alarm_12hr_del+")",self.mainControls_Font, invert = False)
            self.display_1309.draw_line(x_val + 1, y_val + 4, x_val + 17, y_val+4, invert = False)
        else:
            self.display_1309.draw_text(x_val + 2,y_val,"("+pico_rtc.alarm_12hr_del+")",self.mainControls_Font, invert = False)
    
    def drawClockMenu(self):
        #print("drawing Clock Menu")
        path_l = "images/mountain_left_35x25.mono"
        self.display_1309.draw_bitmap(path_l, 128 - 35, 64 - 25, 35, 25, invert=False, rotate=0)
        
        clock_options = ["Back", "Change hour", "Change minute",
                         "Change second","12/24hr","Save"]
        x_val = 10
        y_val = 5
        y_padding = 2
        dy = self.mainControls_Font.height + y_padding
        for option in clock_options:
            if Cursor.cursor_value == self.ClockMenu.options[option][0]:
                self.display_1309.draw_text(x_val,y_val, option,self.mainControls_Font, invert = True)
            else: 
                self.display_1309.draw_text(x_val,y_val, option,self.mainControls_Font, invert = False)
            y_val = y_val + dy
            
        y_val = y_val - 2*dy
        x_val = 15 + self.mainControls_Font.measure_text("12/24HR") 
        if Cursor.cursor_value == self.ClockMenu.options["AM/PM"][0]:
            self.display_1309.draw_text(x_val,y_val, "AM/PM",self.mainControls_Font, invert = True)
        else: 
            self.display_1309.draw_text(x_val,y_val, "AM/PM",self.mainControls_Font, invert = False)
            
        #drawing edit
        
        x_val = 75
        y_val = 0
        self.display_1309.draw_text(x_val,y_val,pico_rtc.timestring,self.mainControls_Font, invert = False)
        hour = pico_rtc.timestring[0:2]
        minute = pico_rtc.timestring[3:5]
        second = pico_rtc.timestring[6:8]
        if self.edit_time_list[0] != -1:
            hour = str(self.edit_time_list[0])
            if self.edit_time_list[0] < 10:
                hour = "0" + hour
                
        if self.edit_time_list[1] != -1:
            minute = str(self.edit_time_list[1])
            if self.edit_time_list[1] < 10:
                minute = "0" + minute
        if self.edit_time_list[2] != -1:
            second = str(self.edit_time_list[2])
            if self.edit_time_list[2] < 10:
                second = "0" + second
        
        x_val = 75
        y_val =  2
        string = hour + " : " + minute + " : " + second
        self.display_1309.draw_text(x_val,y_val,string, self.mainControls_Font, invert = False)
        y_val = y_val + self.mainControls_Font.height + y_padding
        
        if pico_rtc.is_twelve == True:
            self.display_1309.draw_text(x_val,y_val,"(12)", self.mainControls_Font, invert = False)
        else:
            self.display_1309.draw_text(x_val,y_val,"(24)", self.mainControls_Font, invert = False)
            
        
        x_val = x_val + self.mainControls_Font.measure_text("(24)")
        if pico_rtc.is_twelve == False:
            self.display_1309.draw_text(x_val + 2,y_val,"("+pico_rtc.twelve_hr_deleniation+")",self.mainControls_Font, invert = False)
            self.display_1309.draw_line(x_val + 1, y_val + 4, x_val + 17, y_val+4, invert = False)
        else:
            self.display_1309.draw_text(x_val + 2,y_val,"("+pico_rtc.twelve_hr_deleniation+")",self.mainControls_Font, invert = False)
    #drawMainControls    
    def drawMainControls(self):
        
        settings = ["101.9", "Next Alarm:"]
        padding = 10
        y_val = 1
        x_val = 5
        
        settings_icon = "Minimal"
        #settings_icon_width = self.mainControls_Font.measure_text(settings_icon)
        if Cursor.cursor_value == self.MainMenu.options["Brightness"][0]:
            self.display_1309.draw_text(x_val, y_val, settings_icon, self.mainControls_Font, invert = True)
        else:
            self.display_1309.draw_text(x_val, y_val, settings_icon, self.mainControls_Font, invert = False)
 
        #Drawing next alarm
        x_val = x_val + self.mainControls_Font.measure_text(settings_icon) + padding
        alhr_str = ""
        almin_str = ""
        
        #alhr_str = str(pico_rtc.alarm_list[0])
        
        alarmtime = pico_rtc.get_alarmtime_str()
        alhr_str = str(alarmtime[0])    
        almin_str = str(alarmtime[1])
        deleniation = alarmtime[2]
        #print(deleniation)
        
        """
        if pico_rtc.is_twelve == False:
            
        else:
            alhr_str = str(pico_rtc.alarm_list[0])    
            almin_str = str(pico_rtc.alarm_list[1])
            deleniation = pico_rtc.alarm_12hr_del
        """
            
        if len(alhr_str) == 1:
            alhr_str = "0" + alhr_str
        if len(almin_str) == 1:
            almin_str = "0" + almin_str 
        al_str = "Alarm at: " + alhr_str + ":" + almin_str + deleniation
        if Cursor.cursor_value == self.MainMenu.options["Alarms"][0]:
            self.display_1309.draw_text(x_val, y_val, al_str, self.mainControls_Font, invert = True)
        else:
            self.display_1309.draw_text(x_val, y_val, al_str, self.mainControls_Font, invert = False)
        y_val = y_val + int(self.mainControls_Font.height/2)
        dx = self.mainControls_Font.measure_text("00:00(AM)")
        if pico_rtc.alarm_active == False:
            if Cursor.cursor_value == self.MainMenu.options["Alarms"][0]:
                self.display_1309.draw_line(x_val - 1, y_val, x_val + dx + 25, y_val, invert = True)
            else:
                self.display_1309.draw_line(x_val - 1, y_val, x_val + dx + 25, y_val, invert = False)
                
        
        #Drawing Frequency
        freq_str = str(self.current_frequency)+"MHz"
        freq_str_width = self.frequency_font.measure_text(freq_str)
        x_val = int(64 - freq_str_width/2)
        y_val = 50
        if Cursor.cursor_value == self.MainMenu.options["Frequency"][0]:
            self.display_1309.draw_text(x_val, y_val, freq_str, self.frequency_font, invert = True)
        else:
            self.display_1309.draw_text(x_val, y_val, freq_str, self.frequency_font, invert = False)
            
            
    def drawVolumeControl(self):
        padding = 2
        init_x = 5
        rec_width = 80
        rec_height = 4
        sel_line_indicator_offset = 2
        rec_fill = int((rec_width-1)*self.vol_percent)
        rec_x = init_x + self.mainControls_Font.measure_text("MUTE") + padding
        rec_y = 11
        text_y = rec_y-2
        if Cursor.cursor_value == self.mainMenuOptions["MUTE"][0]:
            self.display_1309.draw_text(init_x, text_y, "MUTE", self.mainControls_Font, invert = True)
        else:
            self.display_1309.draw_text(init_x, text_y, "MUTE", self.mainControls_Font, invert = False)
            
        center_mute = text_y + int(self.mainControls_Font.height/2)
        if self.mutex % 2 == 1:
            if Cursor.cursor_value == self.MainMenu.options["MUTE"][0]:
                self.display_1309.draw_line(init_x - 1, center_mute, init_x + self.mainControls_Font.measure_text("MUTE"), center_mute, invert = True)
            else:
                self.display_1309.draw_line(init_x - 1, center_mute, init_x + self.mainControls_Font.measure_text("MUTE"), center_mute, invert = False)

            
        if Cursor.cursor_value == self.mainMenuOptions["Vol"][0]:    
            self.display_1309.draw_text(init_x + self.mainControls_Font.measure_text("MUTE") + 2*padding + rec_width,
                                        text_y, "Vol", self.mainControls_Font, invert = True)
        else:
            self.display_1309.draw_text(init_x + self.mainControls_Font.measure_text("MUTE") + 2*padding + rec_width,
                            text_y, "Vol", self.mainControls_Font, invert = False)     
        
        self.display_1309.draw_rectangle(rec_x,rec_y,rec_width, rec_height)
        lines_coords = [[rec_x, rec_y  + 1],[rec_x + rec_fill, rec_y + 1],
                        [rec_x, rec_y  + 2],[rec_x + rec_fill, rec_y + 2]]
        self.display_1309.draw_lines(lines_coords)
        #draw a line under the volume bar if we are changing the volume
        if self.current_menu == self.VolumeMenu:
            self.display_1309.draw_line(rec_x + 2,rec_y + rec_height +sel_line_indicator_offset,
                                        rec_x + rec_width - 3, rec_y + rec_height +sel_line_indicator_offset)

        #fill in rectangle based on volume settings
        #line
    def writeTime(self):
        
        x = 64 - int(self.clockDisplay_Font.measure_text(pico_rtc.timestring)/2)
        del_x = x + self.clockDisplay_Font.measure_text(pico_rtc.timestring) + 2
        
        if Cursor.cursor_value == self.mainMenuOptions["Time"][0]:
            self.display_1309.draw_text(x, self.clockDisplay_height, pico_rtc.timestring,
                                self.clockDisplay_Font, invert=True)
            if pico_rtc.is_twelve == True:
                self.display_1309.draw_text(del_x,self.clockDisplay_height, pico_rtc.twelve_hr_deleniation,
                                        self.mainControls_Font,invert = True)
        else:
            self.display_1309.draw_text(x, self.clockDisplay_height, pico_rtc.timestring,
                            self.clockDisplay_Font, invert=False)
            if pico_rtc.is_twelve == True:
                self.display_1309.draw_text(del_x,self.clockDisplay_height, pico_rtc.twelve_hr_deleniation,
                                        self.mainControls_Font,invert = False)
            
    def drawMountains(self):
        path_l = "images/mountain_left_35x25.mono"
        path_r = "images/mountain_right_35x25.mono"
        self.display_1309.draw_bitmap(path_r, 0, 64 - 25, 35, 25, invert=False, rotate=0)
        self.display_1309.draw_bitmap(path_l, 128 - 35, 64 - 25, 35, 25, invert=False, rotate=0)
        
    def drawMainMenu(self):
        Cursor.Total_Numof_settings = len(self.mainMenuOptions) #update this
        
        if pico_rtc.alarm_now == True:
            self.goto_alarm_menu()
        # Write the time
        if self.using_lightsensor == True:
            if lightsensor.Light_Value <= 0.026:
                self.goto_minimal_mode()
                #print(lightsensor.Light_Value)
        elif self.using_manual_mode == True:
            self.goto_minimal_mode()
            
        self.drawMountains()
        self.writeTime()
        self.drawVolumeControl()
        self.drawMainControls()
        #print(lightsensor.Light_Value)
        
        
    def drawVolumeMenu(self):
        
        if self.volume != Cursor.sp_cursor_value:
            print("Changing volume to: ", Cursor.sp_cursor_value)
            self.volume = Cursor.sp_cursor_value
            self.fm_radio.SetVolume(self.volume)
            self.vol_percent = self.volume/15
        
        self.drawMainMenu()
        
    def drawFrequencyMenu(self):
        
        cursor_fre = round((self.current_frequency - 88)*10) # This needs to be rounded because changing it to an int without rounding causes unexpected values to appear
        
        if int(cursor_fre) != Cursor.sp_cursor_value:
            
            print(Cursor.sp_cursor_value)
            print(cursor_fre)
            print(int(cursor_fre))
            
            self.current_frequency = float(Cursor.sp_cursor_value/10) + 88
            print("Changing frequency to: ", self.current_frequency)
            self.fm_radio.SetFrequency(self.current_frequency)
         
        self.drawMainMenu()
        
    def drawBrightnessOptionsMenu(self):
        
        self.drawMountains()
        brightness_options = ["Back", "Manual", "Change when dark"]
        x_val = 10
        y_val = 5
        y_padding = 2
        dy = self.mainControls_Font.height + y_padding
        
        for option in brightness_options:
            if Cursor.cursor_value == self.BrightnessMenu.options[option][0]:
                self.display_1309.draw_text(x_val,y_val, option,self.mainControls_Font, invert = True)
            else: 
                self.display_1309.draw_text(x_val,y_val, option,self.mainControls_Font, invert = False)
            y_val = y_val + dy
        y_val = y_val - dy + int(self.mainControls_Font.height/2)
        
        if self.using_lightsensor == False:
            self.display_1309.draw_line(x_val - 2, y_val, x_val + self.mainControls_Font.measure_text(brightness_options[2]) + 2, y_val)  
        
        
    def drawMinimalMode(self):
        if pico_rtc.alarm_now == True:
            self.goto_alarm_menu()
        if self.using_lightsensor == True:
            if lightsensor.Light_Value > 0.034:
                self.goto_main_menu()
        
        #self.drawMountains()
        #print("Drawing minimal mode")
        x = 64 - int(self.frequency_font.measure_text(pico_rtc.timestring)/2)
        del_x = x + self.frequency_font.measure_text(pico_rtc.timestring) + 2
        y = 32 - int(self.frequency_font.height/2)
        self.display_1309.draw_text(x, y, pico_rtc.timestring,
                            self.frequency_font, invert=False)
        
        if pico_rtc.is_twelve == True:
            self.display_1309.draw_text(del_x,y, pico_rtc.twelve_hr_deleniation, self.mainControls_Font,invert = False)
        
        
    def change_menu(self):
        
        if(button_interrupt.Button_Active == True):
            
            for option in self.current_menu.options.values():
                if option[0] == Cursor.cursor_value:
                    option[1]()
        button_interrupt.Button_Active = False
        
             
      


