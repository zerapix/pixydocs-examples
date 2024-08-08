from zscript import dataset
from rapidfuzz import process, fuzz


def log_unable_to_find_vendor():
    log_flag('error', 'Unable to Find Vendor', 'Could not find the vendor for this document. Please verify that the Vendor and Vendor Address fields are filled out correctly.')


# This rule picks the right vendor from the Vendor List using the chips applied
# to the Vendor field in combination with the Vendor Address field value.
# If it cannot find the right vendor, it will flag the document with an error flag.
# If the vendor is inactive, it will flag the document with an error flag.
def get_vendor(value, field, needed_fields):
    parent_data_list_id = field['params']['data_list_id']
    child_list_dataset = dataset.bound_list_dataset__for_root_id(parent_data_list_id)

    # Get the Vendor Name field value
    vendor_name = value["value"]
    
    vendor_address_field = needed_fields["Vendor Address"]
    vendor_address_value = vendor_address_field['manual_value'] if vendor_address_field['manual_value'] is not None else vendor_address_field['value']
    vendor_address_json = vendor_address_field['manual_value_json'] or vendor_address_field['value_json']

    no_value = {
        'value': None,
        'ref_id': None
    }

    if not vendor_name and not vendor_address_value:
        log_unable_to_find_vendor()
        return no_value

    columns_dict = dataset.list_dataset__for_id(parent_data_list_id).column_ids__mapped_by_name
    matched_vendor_entry = None
    entries_to_check = child_list_dataset.values
    vendor_entries_by_name = {}

    if vendor_address_value and vendor_address_json:
        vendor_address_components = vendor_address_json.get('us_address')
        # MARK: Search for an address match across all entries in the Vendor List where the Default Location is set to 'True'
        address_match_entries = {}
        for entry in child_list_dataset.values:
            street_match = False
            city_match = False
            state_match = False
            default_location_match = False
            for cell in entry.data_list_entry_cells:
                # See if we can match the street
                if cell.data_list_column_id == columns_dict['Street Address']:
                    for cell_value in cell.data_list_entry_cell_values:
                        value_in_cell_value = cell_value.value
                        if value_in_cell_value and value_in_cell_value.lower() == vendor_address_components['street1'].lower():
                            street_match = True
                            break
                # If the street was matched, see if we can match the city
                if cell.data_list_column_id == columns_dict['City']:
                    for cell_value in cell.data_list_entry_cell_values:
                        value_in_cell_value = cell_value.value
                        if value_in_cell_value and value_in_cell_value.lower() == vendor_address_components['city'].lower():
                            city_match = True
                            break
                # If the city was matched, see if we can match the state
                if cell.data_list_column_id == columns_dict['State']:
                    for cell_value in cell.data_list_entry_cell_values:
                        value_in_cell_value = cell_value.value
                        if value_in_cell_value and value_in_cell_value.lower() == vendor_address_components['state'].lower():
                            state_match = True
                            break

                # Check if default_location is True
                if cell.data_list_column_id == columns_dict['Default Location']:
                    for cell_value in cell.data_list_entry_cell_values:
                        if cell_value.value == 'True':
                            default_location_match = True
                            break
                
            # If all conditions are satisfied, add the entry and break out of the loop
            if street_match and city_match and state_match and default_location_match:
                address_match_entries[entry.id] = entry
                break
        
        if not address_match_entries:
            log_flag('error', 'Unable to Find Vendor', 'A Vendor Address was provided, but no matches were found in the Vendor list.')
            return no_value

        if len(address_match_entries) == 1:
            matched_vendor_entry = list(address_match_entries.values())[0]
        # If we find more than one match, skip to the name fuzzy match but only use the entries where the address matched
        else:
            entries_to_check = list(address_match_entries.values())

    if not matched_vendor_entry:
        if not vendor_name:
            log_unable_to_find_vendor()
            return no_value
        for entry in entries_to_check:
            for cell in entry.data_list_entry_cells:
                if cell.data_list_column_id == columns_dict['Vendor Name']:
                    for cell_value in cell.data_list_entry_cell_values:
                        value_in_cell_value = cell_value.value
                        if not value_in_cell_value:
                            continue
                        vendor_entries_by_name[value_in_cell_value.lower()] = entry

        # Fuzzy match on the name of the vendor
        # There may be multiple matches (i.e. multiple Home Depots in the list, etc.)
        vendor_name_matches = process.extract(
                                vendor_name.lower(),
                                vendor_entries_by_name.keys(),
                                scorer=fuzz.WRatio, score_cutoff=90
                            )

        
        # If there is only one match, we can assume that is the correct vendor
        if len(vendor_name_matches) == 1:
            matched_vendor_name = vendor_name_matches[0][0]
            matched_vendor_entry = vendor_entries_by_name[matched_vendor_name]
        else:
            if not vendor_name_matches:
                log_flag('error', 'Unable to Find Vendor', f'Could not find the vendor "{vendor_name}" in the Vendor List. Please verify that the vendor exists in the Vendor List.')
            else:
                log_flag('error', 'Found Multiple Vendor Matches', 'Found multiple vendors that match the vendor name. Please select the correct vendor from the list.')
            return no_value
    
    column_names = field['params']['data_list_column_names']

    # Flag if vendor is inactive
    for cell in matched_vendor_entry.data_list_entry_cells:
        if cell.data_list_column_id == columns_dict['Status']:
            value_in_cell_value = cell.data_list_entry_cell_values[0].value
            if value_in_cell_value.lower() != 'active':
                log_flag('error', 'Inactive Vendor', 'This vendor is marked as inactive.')

    values_by_column = []
    has_at_least_one_value = False
    for column_name in column_names:
        column_id = columns_dict[column_name]
        cell = next((cell for cell in matched_vendor_entry.data_list_entry_cells if cell.data_list_column_id == column_id), None)
        
        value_in_cell_value = ''
        if cell and cell.data_list_entry_cell_values:
            value_in_cell_value = cell.data_list_entry_cell_values[0].value
        values_by_column.append(value_in_cell_value)
        if not has_at_least_one_value and value_in_cell_value:
            has_at_least_one_value = True

    return {
        'value': ' - '.join(values_by_column) if has_at_least_one_value else '',
        'ref_id': str(matched_vendor_entry.id)
    }
