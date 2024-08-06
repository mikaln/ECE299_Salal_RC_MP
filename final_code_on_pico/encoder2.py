from machine import Pin, Timer
import Cursor

EncoderPinA = Pin(4,Pin.IN)
EncoderPinB = Pin(5,Pin.IN)


StateA = 0
StateB = 0




incremented = False
def timer_callback(tim):
    global incremented
    incremented = False

tim = Timer()
#tim.init(mode=Timer.ONE_SHOT, period=100, callback=timer_callback)


def EncoderPinAInterrupt(PinA):
    try:
        global StateA, StateB, incremented, timer_callback,tim
        PinFlags = PinA.irq().flags()
        
        if(PinFlags & 0x0C) == 8:
            #rising edge
            StateA = 1
            if (StateA==1) and (StateB == 0) and (incremented == False):
                Cursor.Change_Cursor_Value(1)
                #print("CCW")
                incremented = True
                tim.init(mode=Timer.ONE_SHOT, period=100, callback=timer_callback)
            
        elif(PinFlags & 0x0C) == 4:
            #falling edge
            StateA = 0
    except:
        print("Exception in EncoderPinAInterrupt")
        
        

def EncoderPinBInterrupt(PinB):
    try:
        global StateA, StateB,incremented, timer_callback,tim, Change_Cursor_Value
        PinFlags = PinB.irq().flags()
        
        if(PinFlags & 0x0C) == 8:
            #rising edge
            StateB = 1
            if (StateA==0) and (StateB == 1) and incremented == False:
                Cursor.Change_Cursor_Value(-1)
                #print("CW")
                incremented = True
                tim.init(mode=Timer.ONE_SHOT, period=100, callback=timer_callback)
            
        elif(PinFlags & 0x0C) == 4:
            #falling edge
            StateB = 0
    except:
        print("Exception in EncoderPinBInterrupt")
    
        
EncoderPinA.irq(handler = EncoderPinAInterrupt, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING,
                hard = True)


EncoderPinB.irq(handler = EncoderPinBInterrupt, trigger = Pin.IRQ_FALLING|Pin.IRQ_RISING,
                hard = True)


