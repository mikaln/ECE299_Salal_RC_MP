"""from machine import ADC
from time import sleep 
LightPin = ADC(28)


while True:
    Light_Value = LightPin.read_u16()
    print(Light_Value)
    sleep(0.25)
"""
from machine import ADC, Timer
#import LightSensor
        
LightPin = ADC(28)
Light_Value = 0.0

def LightSensorHandler(timer):
    
    global LightPin, Light_Value
    
    Light_Value_Digi = LightPin.read_u16()
    Light_Value = Light_Value_Digi*3.3/65536
    print("Light Value: ", Light_Value )  

tim = Timer()
tim.init(mode=Timer.PERIODIC, period=2000, callback=LightSensorHandler)
print("Timer initialized")
