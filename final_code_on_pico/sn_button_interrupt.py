from machine import Pin, Timer
import time

button = Pin(3, Pin.IN, Pin.PULL_UP)
Button_Active = False
Button_Pending = False
first_rise_time = 0
button_pressed = False

button_last = time.ticks_ms()
def button_int_handler_rise(pin):
    global Button_Active, button_last
    if time.ticks_diff(time.ticks_ms(), button_last) > 200:
        Button_Active = True
        button_last = time.ticks_ms()
    
        
button.irq(trigger = Pin.IRQ_RISING, handler = button_int_handler_rise, hard = True)


print("button init")
