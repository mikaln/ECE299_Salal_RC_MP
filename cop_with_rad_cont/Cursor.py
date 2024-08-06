

cursor_value = 0
Total_Numof_settings = 3

#Special cursor (for volume or other controls) 
max_sp_value = 0
sp_cursor_value = 0
using_sp = False

def Change_Cursor_Value(amount):
    
    global cursor_value, Total_Numof_settings,max_sp_value,sp_cursor_value,using_sp
    
    if using_sp == False:
        new_cursor_val = cursor_value + amount
        #print(amount)
        
        #Rolling off the positive end
        if new_cursor_val > Total_Numof_settings:
            cursor_value = 0
        elif new_cursor_val < 0:
            cursor_value = Total_Numof_settings 
        else:
            cursor_value = new_cursor_val
        print(cursor_value) 
    else:
        new_sp_cursor_val = sp_cursor_value + amount
        
        if new_sp_cursor_val > max_sp_value:
            sp_cursor_value = 0
        elif new_sp_cursor_val < 0:
            sp_cursor_value = max_sp_value 
        else:
            sp_cursor_value = new_sp_cursor_val
        print("sp cursor val: ",sp_cursor_value )
    
     
    """

    # Rolling off the negative end
    elif new_cursor_val < Total_Numof_settings:
        cursor_value = (Total_Numof_settings - amount) + 1
    else:
        cursor_value = new_cursor_val
    print("Cursor value:" + str(cursor_value))
    """

    
    