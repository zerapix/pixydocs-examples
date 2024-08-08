from zscript import dataset

# This rule sets the field to 'Not an Invoice'. This is meant to only run when a document enters the Not an Invoice workflow state.
def set_to_not_an_invoice(value, field):
    parent_data_list_id = field['params']['data_list_id']
    child_list_dataset = dataset.bound_list_dataset__for_root_id(parent_data_list_id)
    entry = child_list_dataset.get_entry_by_column_and_value('Is Invoice?', 'Not an Invoice')

    return {
        'value': 'Not an Invoice',
        'ref_id': str(entry.id)
    }