"""
from machine import PWM, Pin
beeper = PWM(Pin(27))
beeper.freq(1000)
beeper.duty_u16(0xFF)

"""


from machine import Pin
import utime

beeper = Pin(27, Pin.OUT,Pin.PULL_DOWN )

def sound_beeper():
    
    beeper.value(1)

    print("Done")
    
def stop_beeper():
    
    beeper.value(0)



