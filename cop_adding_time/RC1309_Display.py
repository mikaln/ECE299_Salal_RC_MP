from xglcd_font import XglcdFont
from ssd1309 import Display
from machine import Pin,SPI
class RC1309Display:
    
    def initDisplay(self):
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
        
    def updateDisplay(self):
        #
        #Clear buffer
        #
        self.display_1309.clear()
        #
        # Draw current menu
        #
        drawMainMenu()
        #
        # Transfer the buffer to the display 
        #
        self.display_1309.present()
        
        
    def drawMainMenu(self):
        print("Loading unispace font")
        unispace = XglcdFont('fonts/Unispace12x24.c', 12, 24)
        print("Unspace font loaded")
    
        # Write the time
        display.draw_text(display.width // 2 - text_width // 2,
                  display.height - text_height, "12:36",
                  unispace, invert=True)
            
        
    
        
    