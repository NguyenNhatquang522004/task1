"""
Property validation and truncation utilities for Neo4j
"""
import logging
from src.neo4j_config import (
    get_property_max_length, 
    get_aggressive_max_length, 
    get_emergency_max_length,
    NEO4J_MAX_STRING_PROPERTY_LENGTH,
    NEO4J_MAX_DESCRIPTION_LENGTH,
    NEO4J_MAX_ID_LENGTH
)

def truncate_property_value(value, max_length=None, property_name="unknown", aggressive=False, emergency=False):
    """
    Truncate property value if it exceeds the maximum length
    
    Args:
        value: The property value to check
        max_length: Maximum allowed length (if None, will be determined from property_name)
        property_name: Name of the property for logging
        aggressive: Use aggressive truncation limits
        emergency: Use emergency truncation limits
        
    Returns:
        Truncated value if necessary
    """
    if value is None:
        return value
    
    # Convert to string if not already
    str_value = str(value)
    
    # Determine max length based on property name and mode
    if max_length is None:
        if emergency:
            max_length = get_emergency_max_length(property_name)
        elif aggressive:
            max_length = get_aggressive_max_length(property_name)
        else:
            max_length = get_property_max_length(property_name)
    
    if len(str_value) <= max_length:
        return str_value
    
    # Truncate and add warning
    truncated_value = str_value[:max_length] + "..."
    mode_str = "EMERGENCY" if emergency else ("AGGRESSIVE" if aggressive else "NORMAL")
    logging.warning(f"[{mode_str}] Property '{property_name}' truncated from {len(str_value)} to {len(truncated_value)} characters")
    
    return truncated_value

def validate_and_clean_entity_properties(entity_dict, aggressive=False, emergency=False):
    """
    Validate and clean entity properties to prevent index errors
    
    Args:
        entity_dict: Dictionary representing an entity
        aggressive: Use aggressive truncation
        emergency: Use emergency truncation
        
    Returns:
        Cleaned entity dictionary
    """
    if not isinstance(entity_dict, dict):
        return entity_dict
    
    cleaned_entity = {}
    
    for key, value in entity_dict.items():
        # Use dynamic truncation based on property name and mode
        cleaned_entity[key] = truncate_property_value(value, None, key, aggressive, emergency)
    
    return cleaned_entity

def validate_and_clean_relationship_properties(relationship_dict, aggressive=False, emergency=False):
    """
    Validate and clean relationship properties
    
    Args:
        relationship_dict: Dictionary representing a relationship
        aggressive: Use aggressive truncation
        emergency: Use emergency truncation
        
    Returns:
        Cleaned relationship dictionary
    """
    if not isinstance(relationship_dict, dict):
        return relationship_dict
    
    cleaned_relationship = {}
    
    for key, value in relationship_dict.items():
        # Use dynamic truncation based on property name and mode
        cleaned_relationship[key] = truncate_property_value(value, None, key, aggressive, emergency)
    
    return cleaned_relationship

def validate_graph_document(graph_document, aggressive=False, emergency=False):
    """
    Validate and clean all entities and relationships in a graph document
    
    Args:
        graph_document: GraphDocument object
        aggressive: Use aggressive truncation
        emergency: Use emergency truncation
        
    Returns:
        Cleaned GraphDocument object
    """
    try:
        # Clean nodes/entities
        if hasattr(graph_document, 'nodes') and graph_document.nodes:
            for node in graph_document.nodes:
                if hasattr(node, 'properties') and node.properties:
                    node.properties = validate_and_clean_entity_properties(node.properties, aggressive, emergency)
                
                # Also check direct attributes
                if hasattr(node, 'id'):
                    node.id = truncate_property_value(node.id, None, "node.id", aggressive, emergency)
        
        # Clean relationships
        if hasattr(graph_document, 'relationships') and graph_document.relationships:
            for relationship in graph_document.relationships:
                if hasattr(relationship, 'properties') and relationship.properties:
                    relationship.properties = validate_and_clean_relationship_properties(relationship.properties, aggressive, emergency)
        
        return graph_document
        
    except Exception as e:
        logging.error(f"Error validating graph document: {e}")
        return graph_document

def validate_graph_documents_list(graph_documents, aggressive=False, emergency=False):
    """
    Validate and clean a list of graph documents
    
    Args:
        graph_documents: List of GraphDocument objects
        aggressive: Use aggressive truncation
        emergency: Use emergency truncation
        
    Returns:
        List of cleaned GraphDocument objects
    """
    if not isinstance(graph_documents, list):
        return graph_documents
    
    cleaned_documents = []
    
    for doc in graph_documents:
        try:
            cleaned_doc = validate_graph_document(doc, aggressive, emergency)
            cleaned_documents.append(cleaned_doc)
        except Exception as e:
            logging.error(f"Error cleaning graph document: {e}")
            # Still add the original document to avoid complete failure
            cleaned_documents.append(doc)
    
    return cleaned_documents
