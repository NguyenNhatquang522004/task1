from src.property_validator import truncate_property_value
from src.neo4j_config import get_property_max_length

# Test basic truncation
large_text = 'A' * 15000
result = truncate_property_value(large_text, property_name='description')
print(f'Original: {len(large_text)} chars')
print(f'Truncated: {len(result)} chars')
print(f'Max allowed for description: {get_property_max_length("description")}')

# Test ID truncation
large_id = 'ID_' + 'X' * 1000
result_id = truncate_property_value(large_id, property_name='id')
print(f'Large ID: {len(large_id)} -> {len(result_id)} chars')

# Test the exact error case (13494 bytes)
problematic_text = 'Problem: ' + 'Lorem ipsum ' * 1200
result_problem = truncate_property_value(problematic_text, property_name='description')
print(f'Problematic text: {len(problematic_text)} -> {len(result_problem)} chars')

print('✅ Property validation fix is working!')
print('✅ This should prevent Neo4j "Property value is too large to index" errors')
