import logging
from langchain.docstore.document import Document
import os
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain_groq import ChatGroq
from langchain_google_vertexai import HarmBlockThreshold, HarmCategory
from langchain_experimental.graph_transformers.diffbot import DiffbotGraphTransformer
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_anthropic import ChatAnthropic
from langchain_fireworks import ChatFireworks
from langchain_aws import ChatBedrock
from langchain_community.chat_models import ChatOllama
import boto3
import google.auth
from src.shared.constants import ADDITIONAL_INSTRUCTIONS
from src.shared.llm_graph_builder_exception import LLMGraphBuilderException
from src.gemini_key_manager import create_gemini_llm, get_gemini_key_manager
import re
from typing import List

def get_llm(model: str):
    """Retrieve the specified language model based on the model name."""
    model = model.lower().strip()
    env_key = f"LLM_MODEL_CONFIG_{model}"
    env_value = os.environ.get(env_key)

    if not env_value:
        err = f"Environment variable '{env_key}' is not defined as per format or missing"
        logging.error(err)
        raise Exception(err)
    
    logging.info("Model: {}".format(env_key))
    try:
        if "gemini" in model:
            # Check if we should use API keys or Vertex AI
            use_api_keys = os.getenv('GEMINI_USE_API_KEYS', 'true').lower() == 'true'
            
            if use_api_keys:
                # Use API key rotation system
                model_name = env_value
                logging.info(f"Using Gemini API keys rotation for model: {model_name}")
                llm = create_gemini_llm(model_name=model_name, temperature=0)
            else:
                # Use Vertex AI (original method)
                model_name = env_value
                credentials, project_id = google.auth.default()
                llm = ChatVertexAI(
                    model_name=model_name,
                    #convert_system_message_to_human=True,
                    credentials=credentials,
                    project=project_id,
                    temperature=0,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    },
                )
        elif "openai" in model:
            model_name, api_key = env_value.split(",")
            if "o3-mini" in model:
                llm= ChatOpenAI(
                api_key=api_key,
                model=model_name)
            else:
                llm = ChatOpenAI(
                api_key=api_key,
                model=model_name,
                temperature=0,
                )

        elif "azure" in model:
            model_name, api_endpoint, api_key, api_version = env_value.split(",")
            llm = AzureChatOpenAI(
                api_key=api_key,
                azure_endpoint=api_endpoint,
                azure_deployment=model_name,  # takes precedence over model parameter
                api_version=api_version,
                temperature=0,
                max_tokens=None,
                timeout=None,
            )

        elif "anthropic" in model:
            model_name, api_key = env_value.split(",")
            llm = ChatAnthropic(
                api_key=api_key, model=model_name, temperature=0, timeout=None
            )

        elif "fireworks" in model:
            model_name, api_key = env_value.split(",")
            llm = ChatFireworks(api_key=api_key, model=model_name)

        elif "groq" in model:
            model_name, base_url, api_key = env_value.split(",")
            llm = ChatGroq(api_key=api_key, model_name=model_name, temperature=0)

        elif "bedrock" in model:
            model_name, aws_access_key, aws_secret_key, region_name = env_value.split(",")
            bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=region_name,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
            )

            llm = ChatBedrock(
                client=bedrock_client,region_name=region_name, model_id=model_name, model_kwargs=dict(temperature=0)
            )

        elif "ollama" in model:
            model_name, base_url = env_value.split(",")
            llm = ChatOllama(base_url=base_url, model=model_name)

        elif "diffbot" in model:
            #model_name = "diffbot"
            model_name, api_key = env_value.split(",")
            llm = DiffbotGraphTransformer(
                diffbot_api_key=api_key,
                extract_types=["entities", "facts"],
            )
        
        else: 
            model_name, api_endpoint, api_key = env_value.split(",")
            llm = ChatOpenAI(
                api_key=api_key,
                base_url=api_endpoint,
                model=model_name,
                temperature=0,
            )
    except Exception as e:
        err = f"Error while creating LLM '{model}': {str(e)}"
        logging.error(err)
        raise Exception(err)
 
    logging.info(f"Model created - Model Version: {model}")
    return llm, model_name

def get_llm_model_name(llm):
    """Extract name of llm model from llm object"""
    for attr in ["model_name", "model", "model_id"]:
        model_name = getattr(llm, attr, None)
        if model_name:
            return model_name.lower()
    print("Could not determine model name; defaulting to empty string")
    return ""

def get_combined_chunks(chunkId_chunkDoc_list, chunks_to_combine):
    combined_chunk_document_list = []
    combined_chunks_page_content = [
        "".join(
            document["chunk_doc"].page_content
            for document in chunkId_chunkDoc_list[i : i + chunks_to_combine]
        )
        for i in range(0, len(chunkId_chunkDoc_list), chunks_to_combine)
    ]
    combined_chunks_ids = [
        [
            document["chunk_id"]
            for document in chunkId_chunkDoc_list[i : i + chunks_to_combine]
        ]
        for i in range(0, len(chunkId_chunkDoc_list), chunks_to_combine)
    ]

    for i in range(len(combined_chunks_page_content)):
        combined_chunk_document_list.append(
            Document(
                page_content=combined_chunks_page_content[i],
                metadata={"combined_chunk_ids": combined_chunks_ids[i]},
            )
        )
    return combined_chunk_document_list

def get_chunk_id_as_doc_metadata(chunkId_chunkDoc_list):
    combined_chunk_document_list = [
       Document(
           page_content=document["chunk_doc"].page_content,
           metadata={"chunk_id": [document["chunk_id"]]},
       )
       for document in chunkId_chunkDoc_list
   ]
    return combined_chunk_document_list
      

async def get_graph_document_list(
    llm, combined_chunk_document_list, allowedNodes, allowedRelationship, additional_instructions=None, schema=None, triplet=None
):
    if additional_instructions:
        additional_instructions = sanitize_additional_instruction(additional_instructions)
    
    # Load schema-specific triplets if schema is provided
    effective_allowed_relationships = allowedRelationship
    if schema and triplet and schema != 'default':
        logging.info(f"Using schema-specific triplets for schema: {schema}")
        try:
            # Load triplet relationships from newSchema.json based on schema
            import json
            import os
            
            schema_file_path = os.path.join(os.path.dirname(__file__), "../..", "frontend", "src", "assets", "newSchema.json")
            if os.path.exists(schema_file_path):
                with open(schema_file_path, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                
                # Find matching schema
                schema_triplets = []
                for item in schema_data:
                    if item.get('schema') == schema:
                        schema_triplets = item.get('triplet', [])
                        break
                
                if schema_triplets:
                    logging.info(f"Found {len(schema_triplets)} triplets for schema '{schema}'")
                    # Convert triplets to allowed_relationships format
                    schema_relationships = []
                    for triplet_str in schema_triplets:
                        if '->' in triplet_str:
                            parts = triplet_str.split('->')
                            if len(parts) == 2:
                                source_rel = parts[0].split('-')
                                target = parts[1].strip()
                                if len(source_rel) >= 2:
                                    source = source_rel[0].strip()
                                    relation = '-'.join(source_rel[1:]).strip()
                                    
                                    # Validate that source and target are in allowedNodes
                                    if (allowedNodes is None or 
                                        (source in allowedNodes and target in allowedNodes)):
                                        schema_relationships.append((source, relation, target))
                                        logging.debug(f"Added valid triplet: ({source}, {relation}, {target})")
                                    else:
                                        logging.warning(f"Skipping triplet due to node validation: {source} -> {relation} -> {target}")
                    
                    if schema_relationships:
                        effective_allowed_relationships = schema_relationships
                        logging.info(f"Using {len(schema_relationships)} validated relationships from schema '{schema}'")
                    else:
                        logging.warning(f"No valid triplets found for schema '{schema}' after validation, using fallback")
                        # Fallback to simple relationship strings from schema
                        try:
                            for item in schema_data:
                                if item.get('schema') == schema:
                                    schema_simple_relationships = item.get('relationshipTypes', [])
                                    if schema_simple_relationships:
                                        effective_allowed_relationships = schema_simple_relationships
                                        logging.info(f"Using {len(schema_simple_relationships)} simple relationships from schema '{schema}'")
                                    break
                        except Exception as fallback_error:
                            logging.error(f"Fallback schema loading error: {fallback_error}")
                else:
                    logging.warning(f"No triplets found for schema '{schema}', trying simple relationships")
                    # Try to use simple relationshipTypes instead
                    try:
                        for item in schema_data:
                            if item.get('schema') == schema:
                                schema_simple_relationships = item.get('relationshipTypes', [])
                                if schema_simple_relationships:
                                    effective_allowed_relationships = schema_simple_relationships
                                    logging.info(f"Using {len(schema_simple_relationships)} simple relationships from schema '{schema}'")
                                break
                    except Exception as simple_error:
                        logging.error(f"Simple schema loading error: {simple_error}")
            else:
                logging.warning(f"Schema file not found: {schema_file_path}")
        except Exception as e:
            logging.error(f"Error loading schema triplets: {e}")
            logging.info("Falling back to original allowed relationships")
    
    # Validate effective_allowed_relationships format before using with LLMGraphTransformer
    validated_relationships = effective_allowed_relationships
    if effective_allowed_relationships:
        try:
            # Check if it's a list of tuples (3-item format)
            if isinstance(effective_allowed_relationships[0], tuple):
                logging.info(f"Validating {len(effective_allowed_relationships)} relationship tuples")
                valid_tuples = []
                for rel in effective_allowed_relationships:
                    if (isinstance(rel, tuple) and len(rel) == 3 and
                        isinstance(rel[0], str) and isinstance(rel[1], str) and isinstance(rel[2], str)):
                        # Check if source and target nodes are in allowedNodes (if specified)
                        if allowedNodes is None or (rel[0] in allowedNodes and rel[2] in allowedNodes):
                            valid_tuples.append(rel)
                        else:
                            logging.warning(f"Skipping invalid tuple (nodes not in allowedNodes): {rel}")
                    else:
                        logging.warning(f"Skipping malformed tuple: {rel}")
                
                if valid_tuples:
                    validated_relationships = valid_tuples
                    logging.info(f"Using {len(valid_tuples)} validated relationship tuples")
                else:
                    logging.warning("No valid relationship tuples found, falling back to strings")
                    # Fallback to just the relationship names as strings
                    validated_relationships = [rel[1] for rel in effective_allowed_relationships if isinstance(rel, tuple) and len(rel) >= 2]
                    if not validated_relationships:
                        validated_relationships = None
                        logging.warning("Could not extract relationship strings from tuples")
            
            # If it's a list of strings, just validate they are strings
            elif isinstance(effective_allowed_relationships[0], str):
                validated_relationships = [rel for rel in effective_allowed_relationships if isinstance(rel, str) and rel.strip()]
                logging.info(f"Using {len(validated_relationships)} string relationships")
            
            else:
                logging.error(f"Unknown relationship format: {type(effective_allowed_relationships[0])}")
                validated_relationships = None
                
        except (IndexError, TypeError) as e:
            logging.error(f"Error validating relationships: {e}")
            validated_relationships = None
    
    logging.info(f"Final validated_relationships type: {type(validated_relationships)}")
    if validated_relationships:
        logging.info(f"Final validated_relationships count: {len(validated_relationships)}")
        if validated_relationships:
            logging.info(f"Sample relationship: {validated_relationships[0]} (type: {type(validated_relationships[0])})")
    
    graph_document_list = []
    if "diffbot_api_key" in dir(llm):
        llm_transformer = llm
    else:
        if "get_name" in dir(llm) and llm.get_name() != "ChatOpenAI" or llm.get_name() != "ChatVertexAI" or llm.get_name() != "AzureChatOpenAI":
            node_properties = False
            relationship_properties = False
        else:
            node_properties = ["description"]
            relationship_properties = ["description"]
        TOOL_SUPPORTED_MODELS = {"qwen3", "deepseek"} 
        model_name = get_llm_model_name(llm)
        ignore_tool_usage = not any(pattern in model_name for pattern in TOOL_SUPPORTED_MODELS)
        logging.info(f"Keeping ignore tool usage parameter as {ignore_tool_usage}")
        
        try:
            llm_transformer = LLMGraphTransformer(
                llm=llm,
                node_properties=node_properties,
                relationship_properties=relationship_properties,
                allowed_nodes=allowedNodes,
                allowed_relationships=validated_relationships,
                ignore_tool_usage=ignore_tool_usage,
                additional_instructions=additional_instructions if additional_instructions else ADDITIONAL_INSTRUCTIONS
            )
        except ValueError as ve:
            logging.error(f"Error creating LLMGraphTransformer with validated relationships: {ve}")
            # Final fallback - try with no relationship constraints
            logging.info("Attempting final fallback with no relationship constraints")
            try:
                llm_transformer = LLMGraphTransformer(
                    llm=llm,
                    node_properties=node_properties,
                    relationship_properties=relationship_properties,
                    allowed_nodes=allowedNodes,
                    allowed_relationships=None,  # Remove all relationship constraints
                    ignore_tool_usage=ignore_tool_usage,
                    additional_instructions=additional_instructions if additional_instructions else ADDITIONAL_INSTRUCTIONS
                )
                logging.info("Successfully created LLMGraphTransformer without relationship constraints")
            except Exception as final_error:
                logging.error(f"Final fallback also failed: {final_error}")
                raise
        except Exception as e:
            logging.error(f"Unexpected error creating LLMGraphTransformer: {e}")
            raise
    
    if isinstance(llm,DiffbotGraphTransformer):
        graph_document_list = llm_transformer.convert_to_graph_documents(combined_chunk_document_list)
    else:
        graph_document_list = await llm_transformer.aconvert_to_graph_documents(combined_chunk_document_list)
    return graph_document_list

async def get_graph_from_llm(model, chunkId_chunkDoc_list, allowedNodes, allowedRelationship, chunks_to_combine, additional_instructions=None, schema=None, triplet=None):
   try:
       llm, model_name = get_llm(model)
       logging.info(f"Using model: {model_name}")
    
       combined_chunk_document_list = get_combined_chunks(chunkId_chunkDoc_list, chunks_to_combine)
       logging.info(f"Combined {len(combined_chunk_document_list)} chunks")
    
       # Parse allowed nodes - handle different input formats
       if isinstance(allowedNodes, str):
           allowed_nodes = [node.strip() for node in allowedNodes.split(',') if node.strip()]
       elif isinstance(allowedNodes, list):
           allowed_nodes = allowedNodes
       elif allowedNodes is None:
           allowed_nodes = []
       else:
           logging.warning(f"Unexpected allowedNodes type: {type(allowedNodes)}. Using empty list.")
           allowed_nodes = []
       logging.info(f"Allowed nodes: {allowed_nodes}")
    
       # Parse allowed relationships - handle different input formats and validate properly
       allowed_relationships = []
       logging.info(f"Raw allowedRelationship input: {allowedRelationship} (type: {type(allowedRelationship)})")
       
       if allowedRelationship is not None and allowedRelationship != "":
           # Handle string input
           if isinstance(allowedRelationship, str):
               # Skip empty strings or strings with just whitespace
               if allowedRelationship.strip():
                   items = [item.strip() for item in allowedRelationship.split(',') if item.strip()]
                   if len(items) % 3 != 0:
                       logging.warning(f"allowedRelationship string has {len(items)} items, not a multiple of 3. Using empty relationships.")
                       allowed_relationships = []
                   else:
                       for i in range(0, len(items), 3):
                           source, relation, target = items[i:i + 3]
                           if source not in allowed_nodes or target not in allowed_nodes:
                               logging.warning(f"Invalid relationship ({source}, {relation}, {target}): source or target not in allowedNodes. Skipping.")
                               continue
                           allowed_relationships.append((source, relation, target))
               else:
                   logging.info("Empty allowedRelationship string provided")
           # Handle list input
           elif isinstance(allowedRelationship, list):
               if len(allowedRelationship) % 3 != 0:
                   logging.warning(f"allowedRelationship list has {len(allowedRelationship)} items, not a multiple of 3. Using empty relationships.")
                   allowed_relationships = []
               else:
                   for i in range(0, len(allowedRelationship), 3):
                       source, relation, target = allowedRelationship[i:i + 3]
                       if source not in allowed_nodes or target not in allowed_nodes:
                           logging.warning(f"Invalid relationship ({source}, {relation}, {target}): source or target not in allowedNodes. Skipping.")
                           continue
                       allowed_relationships.append((source, relation, target))
           else:
               logging.warning(f"Unexpected allowedRelationship type: {type(allowedRelationship)}. Using empty relationships.")
               allowed_relationships = []
           
           logging.info(f"Parsed allowed relationships: {allowed_relationships}")
       else:
           logging.info("No allowed relationships provided (None or empty string)")

       graph_document_list = await get_graph_document_list(
           llm,
           combined_chunk_document_list,
           allowed_nodes,
           allowed_relationships,
           additional_instructions,
           schema,
           triplet
       )
       logging.info(f"Generated {len(graph_document_list)} graph documents")
       return graph_document_list
   except Exception as e:
       logging.error(f"Error in get_graph_from_llm: {e}", exc_info=True)
       raise LLMGraphBuilderException(f"Error in getting graph from llm: {e}")

def sanitize_additional_instruction(instruction: str) -> str:
   """
   Sanitizes additional instruction by:
   - Replacing curly braces `{}` with `[]` to prevent variable interpretation.
   - Removing potential injection patterns like `os.getenv()`, `eval()`, `exec()`.
   - Stripping problematic special characters.
   - Normalizing whitespace.
   Args:
       instruction (str): Raw additional instruction input.
   Returns:
       str: Sanitized instruction safe for LLM processing.
   """
   logging.info("Sanitizing additional instructions")
   instruction = instruction.replace("{", "[").replace("}", "]")  # Convert `{}` to `[]` for safety
   # Step 2: Block dangerous function calls
   injection_patterns = [r"os\.getenv\(", r"eval\(", r"exec\(", r"subprocess\.", r"import os", r"import subprocess"]
   for pattern in injection_patterns:
       instruction = re.sub(pattern, "[BLOCKED]", instruction, flags=re.IGNORECASE)
   # Step 4: Normalize spaces
   instruction = re.sub(r'\s+', ' ', instruction).strip()
   return instruction
