from zscript import dataset
import zkit
from functools import cache


@cache
def get_doc_created_at_date(doc_id):
    return zkit.get_obj(f'/v2/pd/documents/{doc_id}', query={'fields__only': 'id,created_at'})['created_at']

# This rule sets the default date to the document upload date if no date is provided.
def set_default_date(value):
    value_str = value['manual_value'] or value['value']
    if not value_str:
        doc_upload_date = get_doc_created_at_date(dataset.doc.id)

        value['value'] = doc_upload_date.split('T')[0]
    return value
