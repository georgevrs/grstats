from lfs_utils.masking_config import LABOUR_FORCE_SUBCATEGORY_MASKING

print('=== DEBUGGING THE MASKING DICTIONARY ===')
print('Looking for the bullshit value:')

# The exact bullshit value from the data
bullshit_key = '"% aged 15+\n(1981-97: 14+)"'
print(f'Key exists: {bullshit_key in LABOUR_FORCE_SUBCATEGORY_MASKING}')

if bullshit_key in LABOUR_FORCE_SUBCATEGORY_MASKING:
    print(f'Value: {LABOUR_FORCE_SUBCATEGORY_MASKING[bullshit_key]}')

print('\nAll keys containing 1981:')
keys_with_1981 = [k for k in LABOUR_FORCE_SUBCATEGORY_MASKING.keys() if '1981' in str(k)]
print(keys_with_1981)

print('\nAll values in the dictionary:')
print(list(LABOUR_FORCE_SUBCATEGORY_MASKING.values()))

print('\nChecking if the nuclear option target exists:')
nuclear_target = 'PERCENT_AGED_15_PLUS_1981_97_14_PLUS'
print(f'Target exists: {nuclear_target in LABOUR_FORCE_SUBCATEGORY_MASKING.values()}')
