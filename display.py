from machine import SPI,Pin

# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class
import framebuf # this is another library for the display.
import button_interrupt
from xglcd_font import XglcdFont
from ssd1309 import Display
import pico_rtc
import Cursor
import encoder2

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
            "Frequency" : [1, self.change_frequency],
            "Alarms": [2, self.set_alarm],
            "Brightness": [3, self.change_brightness],
            "Time": [4, self.change_time],
            "MUTE": [5, self.mute_volume],
            "Vol": [6,self.change_volume]  
            }
        
        """
        self.volumeMenuOptions = {
            "Volume" : []
            }
        """
        
        MainMenu = Menu("Main Menu", self.mainMenuOptions, self.drawMainMenu)
        #VolumeMenu = Menu("Volume Menu", self.volumeMenuOptions, self.drawMainMenu)
        self.menuOptions = {
            "Main Menu" : MainMenu,
            "Volume Menu": (2, 5, self.drawVolumeMenu)}
        
        self.current_menu = self.menuOptions["Main Menu"]
        self.volume = 15
        self.vol_percent = self.volume/15
        self.cursor = 0;
        pico_rtc.start_timing()
        self.volume
        
    def change_frequency(self):
        print("changing frequency")
    def set_alarm(self):
        print("setting alarm")
    def change_brightness(self):
        print("Changing brightness")
    def change_time(self):
        print("changing time")
    def mute_volume(self):
        print("muting volume")
    def change_volume(self):
        print("changing volume")
                   
        
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
        #self.mainControls_Font = XglcdFont('fonts/ArcadePix9x11.c', 9, 11)
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
        #print("Clearing buffers")
        self.display_1309.clear_buffers()
        
        #
        # Update the text on the screen
        #
        #print("updating text")
        self.current_menu.drawing_function()
        #self.drawMainMenu()
        
        #
        # Transfer the buffer to the oled screen
        #
        self.display_1309.present()

    def drawMainControls(self):
        
        settings = ["101.9", "Alarms", "Brightness"]
        #self.cursor = self.cursor % (len(settings) + 1) 
        padding = 8
        y_val = 64 - self.mainControls_Font.height
        x_val = 0
        index = 0
        for setting in settings:
            if index == Cursor.cursor_value -1 :
                self.display_1309.draw_text(x_val, y_val, setting, self.mainControls_Font, invert = True)
            else:
                self.display_1309.draw_text(x_val, y_val, setting, self.mainControls_Font, invert = False)
            x_val = x_val + self.mainControls_Font.measure_text(setting) + padding
            index = index + 1
            
    def drawVolumeControl(self):
        padding = 2
        init_x = 5
        rec_width = 80 
        rec_fill = int((rec_width-1)*self.vol_percent)
        
        if Cursor.cursor_value == self.mainMenuOptions["MUTE"][0]:
            self.display_1309.draw_text(init_x, self.mainControls_Font.height, "MUTE", self.mainControls_Font, invert = True)
        else:
            self.display_1309.draw_text(init_x, self.mainControls_Font.height, "MUTE", self.mainControls_Font, invert = False)
        
        rec_x = init_x + self.mainControls_Font.measure_text("MUTE") + padding
        rec_y = 10
        self.display_1309.draw_rectangle(rec_x,rec_y,rec_width,4)
        lines_coords = [[rec_x, rec_y  + 1],[rec_x + rec_fill, rec_y + 1],
                        [rec_x, rec_y  + 2],[rec_x + rec_fill, rec_y + 2]]
        self.display_1309.draw_lines(lines_coords)
        
        if Cursor.cursor_value == self.mainMenuOptions["Vol"][0]:
            self.display_1309.draw_text(init_x + self.mainControls_Font.measure_text("MUTE") + 2*padding + rec_width,
                                        self.mainControls_Font.height, "Vol", self.mainControls_Font, invert = True)
        else:
            self.display_1309.draw_text(init_x + self.mainControls_Font.measure_text("MUTE") + 2*padding + rec_width,
                            self.mainControls_Font.height, "Vol", self.mainControls_Font, invert = False)
        
        
        #fill in rectangle based on volume settings
        #line
    def writeTime(self):
        #4th setting
        if Cursor.cursor_value == self.mainMenuOptions["Time"][0]:
            self.display_1309.draw_text(15, self.clockDisplay_height, pico_rtc.timestring,
                                self.clockDisplay_Font, invert=True)
        else:
            self.display_1309.draw_text(15, self.clockDisplay_height, pico_rtc.timestring,
                            self.clockDisplay_Font, invert=False)
    def drawMainMenu(self):
        Cursor.Total_Numof_settings = len(self.mainMenuOptions)
        # Write the time
        self.writeTime()
        self.drawVolumeControl()
        self.drawMainControls()
    
    def drawVolumeMenu(self):
        self.drawMainMenu()
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
    def drawBasicDisplay(self):
        self.oled.text("Welcome to ECE", 0, 0) # Print the text starting from 0th column and 0th row
        self.oled.text("299", 45, 10) # Print the number 299 starting at 45th column and 10th row
        self.oled.text("Count is: %4d" % button_interrupt.Count, 0, 30 ) # Print the value stored in the variable Count. 
        #
        # Draw box below the text
        #
        self.oled.rect( 0, 50, 128, 5, 1  )
    
    

            
    


