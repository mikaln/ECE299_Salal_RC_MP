"""SSD1309 demo (images)."""
from time import sleep
from machine import Pin, SPI  # type: ignore
from ssd1309 import Display


def test():
    """Test code."""
    spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
    spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
    spi_res = Pin(16) # res stands for reset; to be connected to a free GPIO pin
    spi_dc  = Pin(17) # dc stands for data/command; to be connected to a free GPIO pin
    spi_cs  = Pin(20) # chip select; to be connected to the SPI chip select of the Pico 
    
    """Test code."""
    spi = SPI(0, baudrate=10000000, sck=spi_sck, mosi=spi_sda)
    display = Display(spi, dc=spi_dc, cs=spi_cs, rst=spi_res)
    # i2c = I2C(0, freq=400000, scl=Pin(5), sda=Pin(4))  # Pico I2C bus 1
    # display = Display(i2c=i2c, rst=Pin(2))

    display.draw_bitmap("images/eyes_128x42.mono", 0, display.height // 2 - 21,
                        128, 42)
    display.present()
    sleep(5)

    display.clear_buffers()
    display.draw_bitmap("images/doggy_jet128x64.mono", 0, 0, 128, 64,
                        invert=True)
    display.present()
    sleep(5)

    display.clear_buffers()
    display.draw_bitmap("images/invaders_48x36.mono", 0, 14, 48, 36, rotate=90)
    display.draw_bitmap("images/invaders_48x36.mono", 40, 14, 48, 36)
    display.draw_bitmap("images/invaders_48x36.mono", 92, 14, 48, 36,
                        rotate=270)
    display.present()

    sleep(10)
    display.cleanup()
    print('Done.')


test()
