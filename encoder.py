from machine import Pin

EncoderPinA = Pin(4,Pin.IN)
EncoderPinB = Pin(5,Pin.IN)


def EncoderPinAInterrupt(PinA):
    global EncoderPinB
    PinFlags = PinA.irq().flags()
    
    if(PinFlags & 0x0C) == 8:
    #print("PIN A: rising edge")
        if EncoderPinB.value() == 0:
            print("CW")
        else:
            print("CCW")
        
    """
    if(PinFlags & 0x0C) == 4:
        #print("PIN A: falling edge")
    elif(PinFlags & 0x0C) == 8:
        #print("PIN A: rising edge")
        if EncoderPinB.value() == 1:
            print("CW")
        else:
            print("CCW")
    elif(PinFlags & 0x0C) == 12:
        #print("PIN A: rising and falling edge")
     """   
0
def EncoderPinBInterrupt(PinB):
    PinFlags = PinB.irq().flags()
        
        """
    if(PinFlags & 0x0C) == 4:
        #print("PIN B: falling edge")
    elif(PinFlags & 0x0C) == 8:
        #print("PIN B: rising edge")
    elif(PinFlags & 0x0C) == 12:
        #print("PIN B: rising and falling edge")
    """
EncoderPinA.irq(handler = EncoderPinAInterrupt, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING,
                hard = True)


EncoderPinB.irq(handler = EncoderPinBInterrupt, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING,
                hard = True)



        
