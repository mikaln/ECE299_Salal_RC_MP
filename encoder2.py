from machine import Pin

EncoderPinA = Pin(4,Pin.IN)
EncoderPinB = Pin(5,Pin.IN)


StateA = 0
StateB = 0
First = ""

def EncoderPinAInterrupt(PinA)
    global StateA, StateB, First
    PinFlags = PinA.irq().flags()
    
    if(PinFlags & 0x0C) == 8:
        #rising edge
        StateA = 1
        if (StateA==0) and (StateB = 1):
            First = "A"
            print("CW")
        
    elif(PinFlags & 0x0C) == 4:
        #falling edge
        StateA = 0
        
        

def EncoderPinBInterrupt(PinB):
    global StateA, StateB, First
    PinFlags = PinB.irq().flags()
    
    if(PinFlags & 0x0C) == 8:
        #rising edge
        StateB = 1
        if (StateA==0) and (StateB == 1):
            First = "B"
            print("CCW")
        
    elif(PinFlags & 0x0C) == 4:
        #falling edge
        StateA = 0
    
        
EncoderPinA.irq(handler = EncoderPinAInterrupt, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING,
                hard = True)


EncoderPinB.irq(handler = EncoderPinBInterrupt, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING,
                hard = True)
