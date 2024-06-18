from machine import Pin, Timer
button = Pin(0, Pin.IN, Pin.PULL_UP)
Button_Active = False

def button_timer_handler(timer):
    global button
    global Button_Active
    #print("In button timer handler")
    
    if button.value() == 1 and not Button_Active:
        print("Button not Active")
        Button_Active = True
        print("Button is now active")     
       
def button_int_handler(x):

    Timer(mode=Timer.ONE_SHOT, period=100, callback=button_timer_handler)

button.irq(trigger = Pin.IRQ_RISING, handler = button_int_handler)   

print("button init")
