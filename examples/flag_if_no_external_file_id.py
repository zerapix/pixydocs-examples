from zscript import dataset
import zkit


# This rule raises a flag if the file does not have a file id in the external_ref object.
def flag_if_no_external_file_id(value):
    doc_id = dataset.doc.id
    doc = zkit.get_obj(
        f'/v2/pd/documents/{doc_id}',
        query={'fields__only': 'id,external_ref'}
    )
    doc_external_ref = doc['external_ref']

    if not doc_external_ref or not doc_external_ref.get('file_id', None):
        log_flag(
            'error', 'No File ID',
            'This document does not have a file_id associated with it. '
            'It will not successfully export.'
        )

    return value