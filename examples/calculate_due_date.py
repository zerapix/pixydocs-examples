import re
import datetime
import zkit
from functools import cache
from zscript import dataset


def extract_number(text):
    """Extracts the number from a text string."""
    match = re.search(r'\d+', text)
    if match:
        return int(match.group())
    return None


def regex_search(string, pattern):
    """Checks if the string contains 'Upon Receipt'"""
    return re.search(pattern, string, re.IGNORECASE)


def add_days_str(start_date_str, days):
    """Adds a specified number of days to a given date string and returns the result as a string.

    Args:
      start_date_str: The starting date as a string.
      days: The number of days to add.

    Returns:
      A string representing the date after adding the specified days in the specified format.
    """

    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = start_date + datetime.timedelta(days=days)
    return end_date.strftime("%Y-%m-%d")


def get_first_of_next_month_as_string(date_str: str):
    """Gets the first day of the next month from a given date as a string.

    Args:
      date: The input date str.

    Returns:
      A string representing the first day of the next month in the format "YYYY-MM-DD".
    """
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    first_of_month_date = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    return first_of_month_date.strftime("%Y-%m-%d")


@cache
def get_doc_created_at_date(doc_id):
    return zkit.get_obj(f'/v2/pd/documents/{doc_id}', query={'fields__only': 'id,created_at'})['created_at']

# Calculates the due date if there isn't a due date already set.
def calculate_due_date(value, field, needed_fields):
    # If we have an original_value, we don't need to calculate the due date
    if value['original_value']:
        return
    
    payment_terms = needed_fields['Payment Terms']
    invoice_date = needed_fields['Invoice Date']
    payment_terms_value = payment_terms['value']
    invoice_date_value = invoice_date['value']

    # If we don't have payment terms, jump ship
    if not payment_terms_value:
        return

    # Possible cases (replace 30 with any number): Net 30, N30, N-30, N 30
    net_match = regex_search(payment_terms_value, r"ne?t?\s?-?\d{1,3}")
    if net_match and invoice_date_value:
        number_of_days = extract_number(net_match.group())
        starting_date = invoice_date_value
        if 'EOM' in payment_terms_value:
            starting_date = get_first_of_next_month_as_string(invoice_date_value)
        return add_days_str(starting_date, number_of_days)

    # Possible cases: 30 days, 5 days, 120 days, etc.
    xx_days_match = regex_search(payment_terms_value, r"\d{1,3} days")
    if xx_days_match:
        number_of_days = extract_number(xx_days_match.group())
        starting_date = invoice_date_value
        if 'EOM' in payment_terms_value:
            starting_date = get_first_of_next_month_as_string(invoice_date_value)
        return add_days_str(starting_date, number_of_days)

    # Possible cases: Upon Receipt, Due Upon Receipt, Upon Receipt of Invoice, On Receipt, Due on receipt, etc.
    upon_receipt_match = regex_search(payment_terms_value, r"u?p?on receipt")
    if upon_receipt_match:
        doc_upload_date = get_doc_created_at_date(dataset.doc.id)
        return doc_upload_date.split('T')[0]

    # If no matches, return None
    return