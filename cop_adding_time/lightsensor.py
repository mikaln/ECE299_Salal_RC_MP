"""from machine import ADC
from time import sleep 
LightPin = ADC(28)


while True:
    Light_Value = LightPin.read_u16()
    print(Light_Value)
    sleep(0.25)
"""
from machine import ADC, Timer

LightPin = ADC(28)

def LightSensorHandler(timer):
    global LightPin
    Light_Value_Digi = LightPin.read_u16()
    Light_Value = Light_Value_Digi*3.3/65536
    print(Light_Value)
    if Light_Value < 0.2:
        print("oOo baby it's spooky ")
    elif Light_Value >2.8:
        print("Don't go to the LIGHT")
 
Timer(mode=Timer.PERIODIC, period=2000, callback=LightSensorHandler)















