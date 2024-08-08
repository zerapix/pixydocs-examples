# Flags the document if it entered to the Export to IIQ state, but no reasons were listed.
def flag_if_not_reason(value):
    value_str = value['manual_value'] or value['value']
    if not value_str:
        log_flag('error', 'No Reasons Listed', 'There are no reasons listed for why this document needs to be exported to the IIQ.', True, 'no_reasons_listed') 

    return value
