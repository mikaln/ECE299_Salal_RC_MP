from machine import Pin

EncoderPinA = Pin(4,Pin.IN)
EncoderPinB = Pin(5,Pin.IN)
CountA = 0
CountB = 0


def EncoderPinAInterrupt(PinA):
    global EncoderPinB
    global CountA
    global CountB
    PinFlagsA = PinA.irq().flags()
    
    if(PinFlagsA & 0x0C) == 8:
        
        #print("PIN A: rising edge")
        
        if CountB == 1:
            print("CW")
            CountB = 0
        else:
            CountA = 1
    elif(PinFlagsA & 0x0C) == 4:
        
        #print("PIN A: rising edge")
        
        if CountB == -1:
            print("CW")
            CountB = 0
        else:
            CountA = -1
        
        
def EncoderPinBInterrupt(PinB):
    PinFlags = PinB.irq().flags()
    global CountA
    global CountB
    
    if(PinFlags & 0x0C) == 8:
        
        #print("PIN B: rising edge")
        
        if CountA == 1:
            print("CCW")
            CountA = 0
        else:
            CountB = 1
    elif(PinFlags & 0x0C) == 4:
        
        #print("PIN B: falling edge")
        
        if CountA == -1:
            print("CCW")
            CountA = 0
        else:
            CountB = -1
   
    
EncoderPinA.irq(handler = EncoderPinAInterrupt, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING,
                hard = True)


EncoderPinB.irq(handler = EncoderPinBInterrupt, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING,
                hard = True)



        
