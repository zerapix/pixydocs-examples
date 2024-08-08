from zscript import dataset
import zkit
from zkit import zcache

def override_gl_account(value, field, needed_fields):
    vendor_field = needed_fields['Vendor']
    vendors_entry_id = vendor_field['manual_ref_id'] or vendor_field['ref_id']

    if not vendors_entry_id:
        return
    
    gl_cache_key = f'default_gl_account_for_{vendors_entry_id}_in_gl_list'
    default_gl_value_dict = zcache.get(gl_cache_key)

    vendor_cache_key = f'default_gl_account_for_{vendors_entry_id}_in_vendor_list'
    default_vendor_value_dict = zcache.get(vendor_cache_key)
    
    # We use cache data when available
    if default_gl_value_dict is not None:
        # if no entry was found, we return "original" value
        if not default_gl_value_dict['ref_id']:
            if default_vendor_value_dict and default_vendor_value_dict['ref_id']:
                log_flag('error', 'Unable to Find Default GL Account', 
                         f'Could not find the list entry for the default GL account for this vendor. Please verify that GL account {default_vendor_value_dict['value']} exists in the GL Accounts list. Please contact Pixydocs support if this problem persists.')
            return value
        else:
            return default_gl_value_dict
        
    
    # Get Default Gl Account Number in Vendors list
    cell_value = zkit.get_first('/v2/pd/data_list_entry_cell_values', query={
        'limit': '1',
        'data_list_entry_cell__data_list_entry_id': vendors_entry_id,
        'data_list_entry_cell__data_list_column__name': 'Default Gl Account Number'
    })
    
    no_entry_dict = {
        'value': '',
        'ref_id': ''
    }
    
    if not cell_value['value']:
        zcache[vendor_cache_key] = no_entry_dict
        zcache[gl_cache_key] = no_entry_dict
        return value
    else:
        zcache[vendor_cache_key] = {
            'value': cell_value['value'],
            'ref_id': vendors_entry_id
        }
        
    parent_data_list_id = field['params']['data_list_id']

    # Get first entry with cells and cell values, in GL list, that matches the vendors Default Gl Account Number
    child_list_dataset = dataset.bound_list_dataset__for_root_id(parent_data_list_id)
    gl_entry = child_list_dataset.get_entry_by_column_and_value('Account Number', cell_value['value'])

    if not gl_entry:
        zcache[gl_cache_key] = no_entry_dict
        log_flag('error', 'Unable to Find Default GL Account', 
                 f'Could not find the list entry for the default GL account for this vendor. Please verify that GL account {cell_value['value']} exists in the GL Accounts list. Please contact Pixydocs support if this problem persists.')
        return value
    
    columns_dict = dataset.list_dataset__for_id(parent_data_list_id).column_ids__mapped_by_name

    column_names = field['params']['data_list_column_names']

    values_by_column = []
    has_at_least_one_value = False
    for column_name in column_names:
        column_id = columns_dict[column_name]
        cell = next((cell for cell in gl_entry.data_list_entry_cells if cell.data_list_column_id == column_id), None)
        
        value= ''
        if cell and cell.data_list_entry_cell_values:
            value = cell.data_list_entry_cell_values[0].value
        values_by_column.append(value)
        if not has_at_least_one_value and value:
            has_at_least_one_value = True

    default_gl_value_dict = {
        'value': ' - '.join(values_by_column) if has_at_least_one_value else '',
        'ref_id': str(gl_entry.id)
    }

    zcache[gl_cache_key] = default_gl_value_dict
        
    return default_gl_value_dict
