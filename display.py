from machine import SPI,Pin

# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class
import framebuf # this is another library for the display.
import button_interrupt

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
        self.menu = "Main Menu"
        self.cursor = 0;
        
    def initDisplay(self):
        print("Init display")
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

    def updateDisplay(self):
        #
        # Clear the buffer
        #
        self.oled.fill(0)
        
        #
        # Update the cursor
        #
        
        self.updateCursor()
        
        #
        # Update the text on the screen
        #
        self.drawSettingsMenu()
        

        #
        # Transfer the buffer to the screen
        #
        self.oled.show()
  
    #print("Updated Display")       
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
    def updateCursor(self):
        if(button_interrupt.Button_Active == True):
            self.cursor = self.cursor + 1
            print("cursor change, cursor number:", self.cursor)
            button_interrupt.Button_Active = False
            #print(button_interrupt.Button_Active)
            
    
