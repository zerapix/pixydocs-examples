def convert_to_float(s):
  try:
    return float(s)
  except ValueError:
    return None

# Flags the field if rate * quantity != amount.
def check_rate_times_quantity(value, field, needed_fields):
    quantity_field = needed_fields["Quantity"]
    rate_field = needed_fields["Rate"]
    
    amount_str = value["value"]
    quantity_str = quantity_field["value"]
    rate_str = rate_field["value"]
    
    # Bow out early if we don't have all three values
    if not amount_str or not quantity_str or not rate_str:
        return value
    
    amount = convert_to_float(amount_str)
    quantity = convert_to_float(quantity_str)
    rate = convert_to_float(rate_str)
    
    if amount and quantity and rate:
        absolute_difference = abs(quantity * rate - amount)
        if absolute_difference >= .01:
            log_flag('error', 'Quantity * Rate does not equal Amount', f'The quantity times the rate ({quantity * rate}) for this line item does not equal the amount ({amount}).')
    
    return value
