from machine import SPI,Pin
import utime

# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class
import framebuf # this is another library for the display.
import button_interrupt
from xglcd_font import XglcdFont
from ssd1309 import Display
import pico_rtc
import Cursor
import encoder2
import radio

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
            "Alarms": [2, self.set_alarm],
            "MUTE": [3, self.mute_volume],
            "Vol": [4,self.goto_volume_menu],
            "Time": [5, self.change_time],
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
            "Go to main menu" : [self.MainMenu.options["Brightness"][0], self.goto_main_menu]
            }
        
        
        
        self.VolumeMenu = Menu("Volume Menu", self.volumeMenuOptions, self.drawVolumeMenu)
        self.FrequencyMenu = Menu("Frequency Menu", self.frequencyMenuOptions, self.drawFrequencyMenu)
        
        self.BrightnessMenu = Menu("Brightness Menu", self.brightnessMenuOptions, self.drawBrightnessMenu)
        
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
        self.fm_radio = radio.Radio(101.9, 1, False) #initializing radio
        self.mutex = 0 #used to track if the radio should be muted or unmuted
        self.dim = 0
        pico_rtc.start_timing()
        

    def goto_main_menu(self):
        #dont forget to make sure you are using the normal cursor
        Cursor.using_sp = False
        #Cursor.cursor_value = 1
        self.current_menu = self.MainMenu
    
    def goto_brightness_menu(self):
        
        self.current_menu = self.BrightnessMenu
        
        print("going to brightness menu")
        
    def change_brightness(self):
        print("Changing brightness")
        
    def change_time(self):
        print("changing time")
        
    def set_alarm(self):
        print("setting alarm")
        
    def mute_volume(self):
        
        self.mutex = self.mutex + 1
        
        if self.mutex % 2 == 0:
            self.fm_radio.SetMute(False)
        else:
            self.fm_radio.SetMute(True)
            
        print("muting volume")
        
    
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

    def drawMainControls(self):
        
        settings = ["101.9", "Next Alarm:"]
        padding = 10
        y_val = 1
        x_val = 5
        
        settings_icon = "Brightness"
        #settings_icon_width = self.mainControls_Font.measure_text(settings_icon)
        if Cursor.cursor_value == self.MainMenu.options["Brightness"][0]:
            self.display_1309.draw_text(x_val, y_val, settings_icon, self.mainControls_Font, invert = True)
        else:
            self.display_1309.draw_text(x_val, y_val, settings_icon, self.mainControls_Font, invert = False)
 
        #Drawing next alarm
        x_val = x_val + self.mainControls_Font.measure_text(settings_icon) + padding
        al_str = "Alarm at: "+self.current_next_alarm + "AM"
        if Cursor.cursor_value == self.MainMenu.options["Alarms"][0]:
            self.display_1309.draw_text(x_val, y_val, al_str, self.mainControls_Font, invert = True)
        else:
            self.display_1309.draw_text(x_val, y_val, al_str, self.mainControls_Font, invert = False)
        
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
            
            self.display_1309.draw_text(del_x,self.clockDisplay_height, self.twelve_hr_deleniation,
                                        self.mainControls_Font,invert = True)
        else:
            self.display_1309.draw_text(x, self.clockDisplay_height, pico_rtc.timestring,
                            self.clockDisplay_Font, invert=False)
            
            self.display_1309.draw_text(del_x,self.clockDisplay_height, self.twelve_hr_deleniation,
                                        self.mainControls_Font,invert = False)
    def drawMountains(self):
        path_r = "images/mountain_right_35x25.mono"
        path_l = "images/mountain_left_35x25.mono"
        self.display_1309.draw_bitmap(path_r, 0, 64 - 25, 35, 25, invert=False, rotate=0)
        self.display_1309.draw_bitmap(path_l, 128 - 35, 64 - 25, 35, 25, invert=False, rotate=0)
        
    def drawMainMenu(self):
        Cursor.Total_Numof_settings = len(self.mainMenuOptions) #update this
        # Write the time
        
        self.drawMountains()
        self.writeTime()
        self.drawVolumeControl()
        self.drawMainControls()
        
    
    def drawVolumeMenu(self):
        if self.volume != Cursor.sp_cursor_value:
            print("Changing volume to: ", Cursor.sp_cursor_value)
            self.volume = Cursor.sp_cursor_value
            self.fm_radio.SetVolume(self.volume)
            self.vol_percent = self.volume/15

        self.drawMainMenu()
        
    def drawFrequencyMenu(self):
        
        #print(Cursor.sp_cursor_value)
        
        cursor_fre = round((self.current_frequency - 88)*10) # This needs to be rounded because changing it to an int without rounding causes unexpected values to appear
        
        #print(cursor_fre)
        #print(int(cursor_fre))
        
        if int(cursor_fre) != Cursor.sp_cursor_value:
            
            self.current_frequency = float(Cursor.sp_cursor_value/10) + 88
            print("Changing frequency to: ", self.current_frequency)
            self.fm_radio.SetFrequency(self.current_frequency)
            
        self.drawMainMenu()
        
    def drawBrightnessMenu(self):
    
        self.drawMountains()
        
        if self.dim == 0:
            self.display_1309.contrast(0)
            print("drawing menu")
            self.dim = 1
        
    def change_menu(self):
        
        if(button_interrupt.Button_Active == True):
            
            for option in self.current_menu.options.values():
                if option[0] == Cursor.cursor_value:
                    option[1]()
        button_interrupt.Button_Active = False
        
             
    def drawSettingsMenu(self):
        settings = ["Time", "Alarms", "Frequency", "Brightness"]
        index = 0 
        RowNum = 0;
        ColNum = 2;
        for setting in settings:
            if index == self.cursor:
                self.oled.text(">"+ setting, ColNum, RowNum)
            else:
                self.oled.text(setting, ColNum, RowNum)
            RowNum = RowNum + 10
            index = index + 1
        
        self.cursor = self.cursor % len(settings)        


