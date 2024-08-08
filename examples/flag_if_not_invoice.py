# Flags the document if it was marked as not an invoice either by the prediction model or manually.
def flag_if_not_invoice(value):
    value_str = value['manual_value'] or value['value']
    if value_str == 'Not an Invoice':
        log_flag('error', 'Not an Invoice', 'This document was marked as not an invoice.', True) 

    return value
