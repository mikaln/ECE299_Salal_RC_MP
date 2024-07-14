from machine import Pin, SPI # SPI is a class associated with the machine library. 
import utime

# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class
import framebuf # this is another library for the display.
import button_interrupt
from display import screen


oledDisplay = screen()
oledDisplay.initDisplay1309()
print("starting")
while ( True ):
    oledDisplay.updateDisplay1309()
    oledDisplay.change_menu()
      
