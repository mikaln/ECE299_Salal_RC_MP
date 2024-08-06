"""
from machine import PWM, Pin
beeper = PWM(Pin(27))
beeper.freq(1000)
beeper.duty_u16(0xFF)

"""


from machine import Pin
beeper = Pin(27, Pin.PULL_UP)
beeper.value(1)
