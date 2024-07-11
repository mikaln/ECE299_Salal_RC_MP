from machine import Pin

EncoderPinA = Pin(4,Pin.IN)
EncoderPinB = Pin(5,Pin.IN)

EncoderPinA.irq(handler = EncoderPinAInterrupt, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING,
                hard = true)


EncoderPinB.irq(handler = EncoderPinBInterrupt, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING,
                hard = true)


def EncoderPinAInterrupt(PinA):
    PinFlags = PinA.irq().flags()
    
    if(PinFlags & 0x0C) == 4:
        print("PIN A: falling edge")
    elif(PinFlags & 0x0C) == 8:
        print("PIN A: rising edge")
    elif(PinFlags & 0x0C) == 12:
        print("PIN A: rising and falling edge")


def EncoderPinBInterrupt(PinB):
    PinFlags = PinB.irq().flags()
    
    if(PinFlags & 0x0C) == 4:
        print("PIN B: falling edge")
    elif(PinFlags & 0x0C) == 8:
        print("PIN B: rising edge")
    elif(PinFlags & 0x0C) == 12:
        print("PIN B: rising and falling edge")
        
