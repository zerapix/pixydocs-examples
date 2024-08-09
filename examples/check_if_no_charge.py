# Checks if the invoice total is less than or equal to zero. Flags the document if so.
def check_if_no_charge(value):
    value_int = None
    try:
        value_int = float(value["value"] or '')
    except ValueError:
        log_flag('error', 'Unable to Verify No-Charge', f"This invoice's total is not a number. Value: {value['value']}")
        return value
        
    if value_int <= 0:
        log_flag('error', 'No-Charge Invoice', "This invoice's total is less than or equal to zero.") 
        
    return value
        
