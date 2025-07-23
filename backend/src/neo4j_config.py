"""
Configuration for property validation and Neo4j limits
"""
import os

# Neo4j property size limits (in characters)
# These can be adjusted based on your Neo4j configuration
NEO4J_MAX_STRING_PROPERTY_LENGTH = int(os.getenv('NEO4J_MAX_STRING_PROPERTY_LENGTH', 8000))
NEO4J_MAX_DESCRIPTION_LENGTH = int(os.getenv('NEO4J_MAX_DESCRIPTION_LENGTH', 5000))
NEO4J_MAX_ID_LENGTH = int(os.getenv('NEO4J_MAX_ID_LENGTH', 500))

# Fallback limits for very large properties
AGGRESSIVE_MAX_LENGTH = int(os.getenv('AGGRESSIVE_MAX_LENGTH', 4000))
EMERGENCY_MAX_LENGTH = int(os.getenv('EMERGENCY_MAX_LENGTH', 2000))

# Properties that are commonly large and should be truncated more aggressively
LARGE_CONTENT_PROPERTIES = {
    'description', 'content', 'text', 'summary', 'body', 'message', 
    'paragraph', 'section', 'excerpt', 'abstract', 'details'
}

# Properties that should be kept shorter (identifiers, names, etc.)
SHORT_PROPERTIES = {
    'id', 'name', 'title', 'label', 'type', 'category', 'tag', 'key'
}

def get_property_max_length(property_name):
    """
    Get the maximum length for a specific property based on its name and type
    
    Args:
        property_name: Name of the property
        
    Returns:
        Maximum allowed length for the property
    """
    property_name_lower = property_name.lower()
    
    if property_name_lower in SHORT_PROPERTIES:
        return NEO4J_MAX_ID_LENGTH
    elif property_name_lower in LARGE_CONTENT_PROPERTIES:
        return NEO4J_MAX_DESCRIPTION_LENGTH
    else:
        return NEO4J_MAX_STRING_PROPERTY_LENGTH

def get_aggressive_max_length(property_name):
    """
    Get aggressive truncation length for properties that still fail validation
    
    Args:
        property_name: Name of the property
        
    Returns:
        Aggressive maximum length
    """
    property_name_lower = property_name.lower()
    
    if property_name_lower in SHORT_PROPERTIES:
        return min(NEO4J_MAX_ID_LENGTH // 2, 250)
    elif property_name_lower in LARGE_CONTENT_PROPERTIES:
        return AGGRESSIVE_MAX_LENGTH
    else:
        return AGGRESSIVE_MAX_LENGTH // 2

def get_emergency_max_length(property_name):
    """
    Get emergency truncation length for properties that repeatedly fail
    
    Args:
        property_name: Name of the property
        
    Returns:
        Emergency maximum length
    """
    property_name_lower = property_name.lower()
    
    if property_name_lower in SHORT_PROPERTIES:
        return 100
    else:
        return EMERGENCY_MAX_LENGTH
