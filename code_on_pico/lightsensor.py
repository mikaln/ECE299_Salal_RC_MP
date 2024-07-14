from machine import ADC
from time import sleep 
LightPin = ADC(28)


while True:
    Light_Value = LightPin.read_u16()
    print(Light_Value)
    sleep(0.25)
















