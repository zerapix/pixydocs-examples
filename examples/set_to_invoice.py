from zscript import dataset

# This rule sets the field to 'Invoice'. This is a temporary fix. NER prediction wipes out "Is An Invoice?" and this just puts the value back in.
def set_to_invoice(value, field):
    parent_data_list_id = field['params']['data_list_id']
    child_list_dataset = dataset.bound_list_dataset__for_root_id(parent_data_list_id)
    entry = child_list_dataset.get_entry_by_column_and_value('Is Invoice?', 'Invoice')

    return {
        'value': 'Invoice',
        'ref_id': str(entry.id)
    }
