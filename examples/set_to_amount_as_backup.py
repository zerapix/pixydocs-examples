# If there isn't a value set, sets the value to whatever Amount is set to.
def set_to_amount_as_backup(value, field, needed_fields):
    amount_field = needed_fields['Amount']
    amount_value = amount_field['manual_value'] or amount_field['value']
    
    # If Rate doesn't have a value and Amount does, use Amount's value.
    if not value['value'] and amount_value:
        return {
            "value": amount_value,
            "ref_id": None
        }
        
    # If Amount got removed and we Rate doesn't have a value, make sure its empty.
    if not value['original_value'] and not amount_value:
        return {
            "value": None,
            "ref_id": None
        }
    
    # If Amount gets updated, update currently mimmicked value.
    if value['value'] and not value['original_value'] and value['value'] != amount_value:
        return {
            "value": amount_value,
            "ref_id": None
        }

    return value
