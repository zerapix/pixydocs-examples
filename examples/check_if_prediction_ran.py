# Checks if the is-an-invoice prediction ran for the document. If not, flags the document.
def check_if_prediction_ran(value):
    if not value['value']:
        log_flag('error', '"Is an Invoice?" Not Set', 'The "Is an Invoice?" field does not have a value. Was the model prediction ran for this document?') 

    return value
