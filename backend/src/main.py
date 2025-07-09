from langchain_neo4j import Neo4jGraph
from src.shared.constants import (BUCKET_UPLOAD,BUCKET_FAILED_FILE, PROJECT_ID, QUERY_TO_GET_CHUNKS, 
                                  QUERY_TO_DELETE_EXISTING_ENTITIES, 
                                  QUERY_TO_GET_LAST_PROCESSED_CHUNK_POSITION,
                                  QUERY_TO_GET_LAST_PROCESSED_CHUNK_WITHOUT_ENTITY,
                                  START_FROM_BEGINNING,
                                  START_FROM_LAST_PROCESSED_POSITION,
                                  DELETE_ENTITIES_AND_START_FROM_BEGINNING,
                                  QUERY_TO_GET_NODES_AND_RELATIONS_OF_A_DOCUMENT)
from src.shared.schema_extraction import schema_extraction_from_text
from dotenv import load_dotenv
from datetime import datetime
import logging
from src.create_chunks import CreateChunksofDocument
from src.graphDB_dataAccess import graphDBdataAccess
from src.document_sources.local_file import get_documents_from_file_by_path
from src.entities.source_node import sourceNode
from src.llm import get_graph_from_llm
from src.document_sources.gcs_bucket import *
from src.document_sources.s3_bucket import *
from src.document_sources.wikipedia import *
from src.document_sources.youtube import *
from src.shared.common_fn import *
from src.make_relationships import *
from src.document_sources.web_pages import *
from src.graph_query import get_graphDB_driver
import re
from langchain_community.document_loaders import WikipediaLoader, WebBaseLoader
import warnings
import sys
import shutil
import urllib.parse
import json
from src.shared.llm_graph_builder_exception import LLMGraphBuilderException

# Import comprehensive logging system
from src.process_logger import create_process_logger, log_process_step, log_processing_step, log_data_transformation
from src.custom_logging_config import (
    create_custom_logging_config, 
    get_custom_formatters, 
    get_custom_hooks,
    create_development_logger,
    create_production_logger
)
import time
import os

# Initialize enhanced logging based on environment
environment = os.getenv('ENVIRONMENT', 'development')
if environment == 'production':
    process_logger = create_production_logger()
elif environment == 'development':
    process_logger = create_development_logger()
else:
    # Use custom configuration
    config = create_custom_logging_config()
    process_logger = create_process_logger(
        log_level=config["log_level"],
        log_directory=config["log_directory"],
        enable_console_logging=config["enable_console_logging"],
        enable_file_logging=config["enable_file_logging"],
        enable_performance_tracking=config["enable_performance_tracking"],
        enable_data_anonymization=config["enable_data_anonymization"],
        max_data_preview_length=config["max_data_preview_length"],
        custom_formatters=get_custom_formatters()
    )
    
    # Add custom hooks for monitoring
    for hook_name, hook_func in get_custom_hooks().items():
        process_logger.add_custom_hook(hook_name, hook_func)

warnings.filterwarnings("ignore")
load_dotenv()
logging.basicConfig(format='%(asctime)s - %(message)s',level='INFO')

def create_source_node_graph_url_s3(graph, model, source_url, aws_access_key_id, aws_secret_access_key, source_type):
    
    lst_file_name = []
    files_info = get_s3_files_info(source_url,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    if len(files_info)==0:
      raise LLMGraphBuilderException('No pdf files found.')
    logging.info(f'files info : {files_info}')
    success_count=0
    failed_count=0
    
    for file_info in files_info:
        file_name=file_info['file_key'] 
        obj_source_node = sourceNode()
        obj_source_node.file_name = file_name.split('/')[-1].strip() if isinstance(file_name.split('/')[-1], str) else file_name.split('/')[-1]
        obj_source_node.file_type = 'pdf'
        obj_source_node.file_size = file_info['file_size_bytes']
        obj_source_node.file_source = source_type
        obj_source_node.model = model
        obj_source_node.url = str(source_url+file_name)
        obj_source_node.awsAccessKeyId = aws_access_key_id
        obj_source_node.created_at = datetime.now()
        obj_source_node.chunkNodeCount=0
        obj_source_node.chunkRelCount=0
        obj_source_node.entityNodeCount=0
        obj_source_node.entityEntityRelCount=0
        obj_source_node.communityNodeCount=0
        obj_source_node.communityRelCount=0
        try:
          graphDb_data_Access = graphDBdataAccess(graph)
          graphDb_data_Access.create_source_node(obj_source_node)
          success_count+=1
          lst_file_name.append({'fileName':obj_source_node.file_name,'fileSize':obj_source_node.file_size,'url':obj_source_node.url,'status':'Success'})

        except Exception as e:
          failed_count+=1
          lst_file_name.append({'fileName':obj_source_node.file_name,'fileSize':obj_source_node.file_size,'url':obj_source_node.url,'status':'Failed'})
    return lst_file_name,success_count,failed_count

def create_source_node_graph_url_gcs(graph, model, gcs_project_id, gcs_bucket_name, gcs_bucket_folder, source_type, credentials):

    success_count=0
    failed_count=0
    lst_file_name = []
    
    lst_file_metadata= get_gcs_bucket_files_info(gcs_project_id, gcs_bucket_name, gcs_bucket_folder, credentials)
    for file_metadata in lst_file_metadata :
      obj_source_node = sourceNode()
      obj_source_node.file_name = file_metadata['fileName'].strip() if isinstance(file_metadata['fileName'], str) else file_metadata['fileName']
      obj_source_node.file_size = file_metadata['fileSize']
      obj_source_node.url = file_metadata['url']
      obj_source_node.file_source = source_type
      obj_source_node.model = model
      obj_source_node.file_type = 'pdf'
      obj_source_node.gcsBucket = gcs_bucket_name
      obj_source_node.gcsBucketFolder = file_metadata['gcsBucketFolder']
      obj_source_node.gcsProjectId = file_metadata['gcsProjectId']
      obj_source_node.created_at = datetime.now()
      obj_source_node.access_token = credentials.token
      obj_source_node.chunkNodeCount=0
      obj_source_node.chunkRelCount=0
      obj_source_node.entityNodeCount=0
      obj_source_node.entityEntityRelCount=0
      obj_source_node.communityNodeCount=0
      obj_source_node.communityRelCount=0
    
      try:
          graphDb_data_Access = graphDBdataAccess(graph)
          graphDb_data_Access.create_source_node(obj_source_node)
          success_count+=1
          lst_file_name.append({'fileName':obj_source_node.file_name,'fileSize':obj_source_node.file_size,'url':obj_source_node.url,'status':'Success', 
                                'gcsBucketName': gcs_bucket_name, 'gcsBucketFolder':obj_source_node.gcsBucketFolder, 'gcsProjectId':obj_source_node.gcsProjectId})
      except Exception as e:
        failed_count+=1
        lst_file_name.append({'fileName':obj_source_node.file_name,'fileSize':obj_source_node.file_size,'url':obj_source_node.url,'status':'Failed', 
                              'gcsBucketName': gcs_bucket_name, 'gcsBucketFolder':obj_source_node.gcsBucketFolder, 'gcsProjectId':obj_source_node.gcsProjectId})
    return lst_file_name,success_count,failed_count

def create_source_node_graph_web_url(graph, model, source_url, source_type):
    success_count=0
    failed_count=0
    lst_file_name = []
    pages = WebBaseLoader(source_url, verify_ssl=False).load()
    if pages==None or len(pages)==0:
      failed_count+=1
      message = f"Unable to read data for given url : {source_url}"
      raise LLMGraphBuilderException(message)
    try:
      title = pages[0].metadata['title'].strip()
      if title:
        graphDb_data_Access = graphDBdataAccess(graph)
        existing_url = graphDb_data_Access.get_websource_url(title)
        if existing_url != source_url:
          title = str(title) + "-" + str(last_url_segment(source_url)).strip()
      else:
        title = last_url_segment(source_url)
      language = pages[0].metadata['language']
    except:
      title = last_url_segment(source_url)
      language = "N/A"

    obj_source_node = sourceNode()
    obj_source_node.file_type = 'text'
    obj_source_node.file_source = source_type
    obj_source_node.model = model
    obj_source_node.url = urllib.parse.unquote(source_url)
    obj_source_node.created_at = datetime.now()
    obj_source_node.file_name = title.strip() if isinstance(title, str) else title
    obj_source_node.language = language
    obj_source_node.file_size = sys.getsizeof(pages[0].page_content)
    obj_source_node.chunkNodeCount=0
    obj_source_node.chunkRelCount=0
    obj_source_node.entityNodeCount=0
    obj_source_node.entityEntityRelCount=0
    obj_source_node.communityNodeCount=0
    obj_source_node.communityRelCount=0
    graphDb_data_Access = graphDBdataAccess(graph)
    graphDb_data_Access.create_source_node(obj_source_node)
    lst_file_name.append({'fileName':obj_source_node.file_name,'fileSize':obj_source_node.file_size,'url':obj_source_node.url,'status':'Success'})
    success_count+=1
    return lst_file_name,success_count,failed_count
  
def create_source_node_graph_url_youtube(graph, model, source_url, source_type):
    
    youtube_url, language = check_url_source(source_type=source_type, yt_url=source_url)
    success_count=0
    failed_count=0
    lst_file_name = []
    obj_source_node = sourceNode()
    obj_source_node.file_type = 'text'
    obj_source_node.file_source = source_type
    obj_source_node.model = model
    obj_source_node.url = youtube_url
    obj_source_node.created_at = datetime.now()
    obj_source_node.chunkNodeCount=0
    obj_source_node.chunkRelCount=0
    obj_source_node.entityNodeCount=0
    obj_source_node.entityEntityRelCount=0
    obj_source_node.communityNodeCount=0
    obj_source_node.communityRelCount=0
    match = re.search(r'(?:v=)([0-9A-Za-z_-]{11})\s*',obj_source_node.url)
    logging.info(f"match value: {match}")
    obj_source_node.file_name = match.group(1)
    transcript= get_youtube_combined_transcript(match.group(1))
    logging.info(f"Youtube transcript : {transcript}")
    if transcript==None or len(transcript)==0:
      message = f"Youtube transcript is not available for : {obj_source_node.file_name}"
      raise LLMGraphBuilderException(message)
    else:  
      obj_source_node.file_size = sys.getsizeof(transcript)
    
    graphDb_data_Access = graphDBdataAccess(graph)
    graphDb_data_Access.create_source_node(obj_source_node)
    lst_file_name.append({'fileName':obj_source_node.file_name,'fileSize':obj_source_node.file_size,'url':obj_source_node.url,'status':'Success'})
    success_count+=1
    return lst_file_name,success_count,failed_count

def create_source_node_graph_url_wikipedia(graph, model, wiki_query, source_type):
  
    success_count=0
    failed_count=0
    lst_file_name=[]
    wiki_query_id, language = check_url_source(source_type=source_type, wiki_query=wiki_query)
    logging.info(f"Creating source node for {wiki_query_id.strip()}, {language}")
    pages = WikipediaLoader(query=wiki_query_id.strip(), lang=language, load_max_docs=1, load_all_available_meta=True).load()
    if pages==None or len(pages)==0:
      failed_count+=1
      message = f"Unable to read data for given Wikipedia url : {wiki_query}"
      raise LLMGraphBuilderException(message)
    else:
      obj_source_node = sourceNode()
      obj_source_node.file_name = wiki_query_id.strip()
      obj_source_node.file_type = 'text'
      obj_source_node.file_source = source_type
      obj_source_node.file_size = sys.getsizeof(pages[0].page_content)
      obj_source_node.model = model
      obj_source_node.url = urllib.parse.unquote(pages[0].metadata['source'])
      obj_source_node.created_at = datetime.now()
      obj_source_node.language = language
      obj_source_node.chunkNodeCount=0
      obj_source_node.chunkRelCount=0
      obj_source_node.entityNodeCount=0
      obj_source_node.entityEntityRelCount=0
      obj_source_node.communityNodeCount=0
      obj_source_node.communityRelCount=0
      graphDb_data_Access = graphDBdataAccess(graph)
      graphDb_data_Access.create_source_node(obj_source_node)
      success_count+=1
      lst_file_name.append({'fileName':obj_source_node.file_name,'fileSize':obj_source_node.file_size,'url':obj_source_node.url, 'language':obj_source_node.language, 'status':'Success'})
    return lst_file_name,success_count,failed_count
    
async def extract_graph_from_file_local_file(uri, userName, password, database, model, merged_file_path, fileName, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):

  logging.info(f'Process file name :{fileName}')
  if not retry_condition:
    gcs_file_cache = os.environ.get('GCS_FILE_CACHE')
    if gcs_file_cache == 'True':
      folder_name = create_gcs_bucket_folder_name_hashed(uri, fileName)
      file_name, pages = get_documents_from_gcs( PROJECT_ID, BUCKET_UPLOAD, folder_name, fileName)
    else:
      file_name, pages, file_extension = get_documents_from_file_by_path(merged_file_path,fileName)
    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'File content is not available for file : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, True, merged_file_path, additional_instructions=additional_instructions)
  else:
    return await processing_source(uri, userName, password, database, model, fileName, [], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, True, merged_file_path, retry_condition, additional_instructions=additional_instructions)
  
async def extract_graph_from_file_s3(uri, userName, password, database, model, source_url, aws_access_key_id, aws_secret_access_key, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
  if not retry_condition:
    if(aws_access_key_id==None or aws_secret_access_key==None):
      raise LLMGraphBuilderException('Please provide AWS access and secret keys')
    else:
      logging.info("Insert in S3 Block")
      file_name, pages = get_documents_from_s3(source_url, aws_access_key_id, aws_secret_access_key)

    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'File content is not available for file : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, additional_instructions=additional_instructions)
  else:
    return await processing_source(uri, userName, password, database, model, file_name, [], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition=retry_condition, additional_instructions=additional_instructions)
  
async def extract_graph_from_web_page(uri, userName, password, database, model, source_url, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
  if not retry_condition:
    pages = get_documents_from_web_page(source_url)
    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'Content is not available for given URL : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, additional_instructions=additional_instructions)
  else:
    return await processing_source(uri, userName, password, database, model, file_name, [], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition=retry_condition, additional_instructions=additional_instructions)
  
async def extract_graph_from_file_youtube(uri, userName, password, database, model, source_url, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
  if not retry_condition:
    file_name, pages = get_documents_from_youtube(source_url)

    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'Youtube transcript is not available for file : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, additional_instructions=additional_instructions)
  else:
     return await processing_source(uri, userName, password, database, model, file_name, [], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition=retry_condition, additional_instructions=additional_instructions)
    
async def extract_graph_from_file_Wikipedia(uri, userName, password, database, model, wiki_query, language, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
  if not retry_condition:
    file_name, pages = get_documents_from_Wikipedia(wiki_query, language)
    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'Wikipedia page is not available for file : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, additional_instructions=additional_instructions)
  else:
    return await processing_source(uri, userName, password, database, model, file_name,[], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition=retry_condition, additional_instructions=additional_instructions)

async def extract_graph_from_file_gcs(uri, userName, password, database, model, gcs_project_id, gcs_bucket_name, gcs_bucket_folder, gcs_blob_filename, access_token, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
  if not retry_condition:
    file_name, pages = get_documents_from_gcs(gcs_project_id, gcs_bucket_name, gcs_bucket_folder, gcs_blob_filename, access_token)
    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'File content is not available for file : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, additional_instructions=additional_instructions)
  else:
    return await processing_source(uri, userName, password, database, model, file_name, [], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition=retry_condition, additional_instructions=additional_instructions)
  
async def processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, is_uploaded_from_local=None, merged_file_path=None, retry_condition=None, additional_instructions=None):
  """
   Extracts a Neo4jGraph from a PDF file based on the model.
   
   Args:
   	 uri: URI of the graph to extract
     db_name : db_name is database name to connect graph db
   	 userName: Username to use for graph creation ( if None will use username from config file )
   	 password: Password to use for graph creation ( if None will use password from config file )
   	 file: File object containing the PDF file to be used
   	 model: Type of model to use ('Diffbot'or'OpenAI GPT')
   
   Returns: 
   	 Json response to API with fileName, nodeCount, relationshipCount, processingTime, 
     status and model as attributes.
  """
  # 🚀 STEP 1: Initialize comprehensive logging with custom metadata
  process_logger.start_process(
    file_name, 
    model, 
    "document_processing",
    custom_metadata={
      'token_chunk_size': token_chunk_size,
      'chunk_overlap': chunk_overlap,
      'chunks_to_combine': chunks_to_combine,
      'allowed_nodes': allowedNodes,
      'allowed_relationships': allowedRelationship,
      'retry_condition': retry_condition,
      'additional_instructions': additional_instructions is not None,
      'is_uploaded_from_local': is_uploaded_from_local,
      'database': database,
      'uri': uri
    }
  )
  
  uri_latency = {}
  response = {}  
  start_time = datetime.now()
  processing_source_start_time = time.time()
  
  # 🔗 STEP 2: Database Connection Setup
  process_logger.log_step(
    "DB_CONNECTION_START",
    "Setting up Neo4j database connection",
    {
      'uri': uri,
      'database': database,
      'username': userName,
      'file_name': file_name,
      'model': model
    }
  )
  
  start_create_connection = time.time()
  graph = create_graph_database_connection(uri, userName, password, database)
  end_create_connection = time.time()
  elapsed_create_connection = end_create_connection - start_create_connection
  
  process_logger.log_step(
    "DB_CONNECTION_COMPLETE",
    "Database connection established successfully",
    {
      'connection_time': f'{elapsed_create_connection:.2f}s',
      'graph_object': str(type(graph)),
      'database': database
    }
  )
  
  logging.info(f'Time taken database connection: {elapsed_create_connection:.2f} seconds')
  uri_latency["create_connection"] = f'{elapsed_create_connection:.2f}'
  
  # 📊 STEP 3: Initialize Data Access Layer
  process_logger.log_step(
    "DATA_ACCESS_INIT",
    "Initializing graph database data access layer",
    {
      'graph_db_access_type': str(type(graphDBdataAccess)),
      'initialization_time': datetime.now().isoformat()
    }
  )
  
  graphDb_data_Access = graphDBdataAccess(graph)
  
  # 🔍 STEP 4: Create Vector Index
  process_logger.log_step(
    "VECTOR_INDEX_CREATE",
    "Creating chunk vector index for similarity search",
    {
      'index_type': 'chunk_vector',
      'purpose': 'similarity_search_and_embeddings'
    }
  )
  
  create_chunk_vector_index(graph)
  # 📄 STEP 5: Document Chunking Process
  process_logger.log_step(
    "CHUNKING_START",
    "Starting document chunking process",
    {
      'file_name': file_name,
      'token_chunk_size': token_chunk_size,
      'chunk_overlap': chunk_overlap,
      'pages_count': len(pages) if pages else 0,
      'retry_condition': retry_condition
    }
  )
  
  start_get_chunkId_chunkDoc_list = time.time()
  total_chunks, chunkId_chunkDoc_list = get_chunkId_chunkDoc_list(graph, file_name, pages, token_chunk_size, chunk_overlap, retry_condition)
  end_get_chunkId_chunkDoc_list = time.time()
  elapsed_get_chunkId_chunkDoc_list = end_get_chunkId_chunkDoc_list - start_get_chunkId_chunkDoc_list
  
  process_logger.log_data_flow(
    "CHUNKING_COMPLETE",
    {
      'input_pages': len(pages) if pages else 0,
      'token_chunk_size': token_chunk_size,
      'chunk_overlap': chunk_overlap
    },
    {
      'total_chunks': total_chunks,
      'chunk_list_length': len(chunkId_chunkDoc_list),
      'first_chunk_sample': chunkId_chunkDoc_list[0] if chunkId_chunkDoc_list else None
    },
    elapsed_get_chunkId_chunkDoc_list
  )
  
  logging.info(f'Time taken to create list chunkids with chunk document: {elapsed_get_chunkId_chunkDoc_list:.2f} seconds')
  uri_latency["create_list_chunk_and_document"] = f'{elapsed_get_chunkId_chunkDoc_list:.2f}'
  uri_latency["total_chunks"] = total_chunks

  # 📊 STEP 6: Document Status Check
  process_logger.log_step(
    "STATUS_CHECK_START",
    "Checking current document processing status",
    {
      'file_name': file_name,
      'purpose': 'determine_processing_state'
    }
  )
  
  start_status_document_node = time.time()
  result = graphDb_data_Access.get_current_status_document_node(file_name)
  end_status_document_node = time.time()
  elapsed_status_document_node = end_status_document_node - start_status_document_node
  
  process_logger.log_step(
    "STATUS_CHECK_COMPLETE",
    "Document status retrieved successfully",
    {
      'status_query_time': f'{elapsed_status_document_node:.2f}s',
      'document_exists': len(result) > 0,
      'current_status': result[0]['Status'] if result else None,
      'processed_chunks': result[0].get('processed_chunk', 0) if result else 0
    }
  )
  
  logging.info(f'Time taken to get the current status of document node: {elapsed_status_document_node:.2f} seconds')
  uri_latency["get_status_document_node"] = f'{elapsed_status_document_node:.2f}'

  select_chunks_with_retry=0
  node_count = 0
  rel_count = 0
      
  if len(result) > 0:
    if result[0]['Status'] != 'Processing':
      # 🔄 STEP 7: Update Document Status to Processing
      process_logger.log_step(
        "STATUS_UPDATE_START",
        "Updating document status to 'Processing'",
        {
          'previous_status': result[0]['Status'],
          'new_status': 'Processing',
          'retry_condition': retry_condition,
          'file_name': file_name
        }
      )
      
      obj_source_node = sourceNode()
      status = "Processing"
      obj_source_node.file_name = file_name.strip() if isinstance(file_name, str) else file_name
      obj_source_node.status = status
      obj_source_node.total_chunks = total_chunks
      obj_source_node.model = model
      if retry_condition == START_FROM_LAST_PROCESSED_POSITION:
          node_count = result[0]['nodeCount']
          rel_count = result[0]['relationshipCount']
          select_chunks_with_retry = result[0]['processed_chunk']
          
          process_logger.log_step(
            "RETRY_RESUME_CONFIG",
            "Configuring retry from last processed position",
            {
              'existing_node_count': node_count,
              'existing_rel_count': rel_count,
              'last_processed_chunk': select_chunks_with_retry,
              'retry_type': 'RESUME_FROM_LAST_POSITION'
            }
          )
      obj_source_node.processed_chunk = 0+select_chunks_with_retry
      logging.info(file_name)
      logging.info(obj_source_node)
      
      start_update_source_node = time.time()
      graphDb_data_Access.update_source_node(obj_source_node)
      graphDb_data_Access.update_node_relationship_count(file_name)
      end_update_source_node = time.time()
      elapsed_update_source_node = end_update_source_node - start_update_source_node
      
      process_logger.log_step(
        "STATUS_UPDATE_COMPLETE",
        "Document status updated successfully",
        {
          'update_time': f'{elapsed_update_source_node:.2f}s',
          'total_chunks': total_chunks,
          'model': model,
          'processed_chunk_start': obj_source_node.processed_chunk
        }
      )
      
      logging.info(f'Time taken to update the document source node: {elapsed_update_source_node:.2f} seconds')
      uri_latency["update_source_node"] = f'{elapsed_update_source_node:.2f}'

      # 🔄 STEP 8: Batch Processing Configuration
      update_graph_chunk_processed = int(os.environ.get('UPDATE_GRAPH_CHUNKS_PROCESSED', '20'))
      
      process_logger.log_step(
        "BATCH_PROCESSING_CONFIG",
        "Configuring batch processing parameters",
        {
          'chunks_per_batch': update_graph_chunk_processed,
          'total_chunks': len(chunkId_chunkDoc_list),
          'batches_expected': len(chunkId_chunkDoc_list) // update_graph_chunk_processed + 1,
          'chunks_to_combine': chunks_to_combine
        }
      )
      
      logging.info('Update the status as Processing')
      is_cancelled_status = False
      job_status = "Completed"
      
      # 🔄 STEP 9: Main Processing Loop
      process_logger.log_step(
        "MAIN_PROCESSING_START",
        "Starting main chunk processing loop",
        {
          'total_chunks_to_process': len(chunkId_chunkDoc_list),
          'batch_size': update_graph_chunk_processed,
          'processing_mode': 'batch_processing'
        }
      )
      for i in range(0, len(chunkId_chunkDoc_list), update_graph_chunk_processed):
        select_chunks_upto = i+update_graph_chunk_processed
        
        process_logger.log_step(
          f"BATCH_{i//update_graph_chunk_processed + 1}_START",
          f"Processing batch {i//update_graph_chunk_processed + 1}",
          {
            'batch_number': i//update_graph_chunk_processed + 1,
            'chunk_range': f'{i}-{select_chunks_upto}',
            'chunks_in_batch': min(update_graph_chunk_processed, len(chunkId_chunkDoc_list) - i)
          }
        )
        
        logging.info(f'Selected Chunks upto: {select_chunks_upto}')
        if len(chunkId_chunkDoc_list) <= select_chunks_upto:
          select_chunks_upto = len(chunkId_chunkDoc_list)
        selected_chunks = chunkId_chunkDoc_list[i:select_chunks_upto]
        
        # 🔍 STEP 10: Cancellation Check
        result = graphDb_data_Access.get_current_status_document_node(file_name)
        is_cancelled_status = result[0]['is_cancelled']
        
        process_logger.log_step(
          f"BATCH_{i//update_graph_chunk_processed + 1}_CANCELLATION_CHECK",
          "Checking for cancellation status",
          {
            'batch_number': i//update_graph_chunk_processed + 1,
            'is_cancelled': bool(is_cancelled_status),
            'current_status': result[0]['Status'] if result else None
          }
        )
        
        logging.info(f"Value of is_cancelled : {result[0]['is_cancelled']}")
        if bool(is_cancelled_status) == True:
          job_status = "Cancelled"
          
          process_logger.log_step(
            "PROCESSING_CANCELLED",
            "Processing cancelled by user",
            {
              'batch_number': i//update_graph_chunk_processed + 1,
              'chunks_processed': i,
              'total_chunks': len(chunkId_chunkDoc_list),
              'cancellation_reason': 'user_request'
            },
            level="WARNING"
          )
          
          logging.info('Exit from running loop of processing file')
          break
        else:
          # 🔄 STEP 11: Process Current Batch
          process_logger.log_step(
            f"BATCH_{i//update_graph_chunk_processed + 1}_PROCESSING",
            f"Processing chunks batch {i//update_graph_chunk_processed + 1}",
            {
              'batch_size': len(selected_chunks),
              'chunk_range': f'{i}-{select_chunks_upto}',
              'allowed_nodes': allowedNodes,
              'allowed_relationships': allowedRelationship,
              'chunks_to_combine': chunks_to_combine
            }
          )
          
          processing_chunks_start_time = time.time()
          node_count,rel_count,latency_processed_chunk = await processing_chunks(selected_chunks,graph,uri, userName, password, database,file_name,model,allowedNodes,allowedRelationship,chunks_to_combine,node_count, rel_count, additional_instructions)
          processing_chunks_end_time = time.time()
          processing_chunks_elapsed_end_time = processing_chunks_end_time - processing_chunks_start_time
          
          process_logger.log_data_flow(
            f"BATCH_{i//update_graph_chunk_processed + 1}_COMPLETE",
            {
              'input_chunks': len(selected_chunks),
              'chunk_range': f'{i}-{select_chunks_upto}',
              'processing_start_time': processing_chunks_start_time
            },
            {
              'node_count': node_count,
              'rel_count': rel_count,
              'latency_details': latency_processed_chunk
            },
            processing_chunks_elapsed_end_time
          )
          
          logging.info(f"Time taken {update_graph_chunk_processed} chunks processed upto {select_chunks_upto} completed in {processing_chunks_elapsed_end_time:.2f} seconds for file name {file_name}")
          uri_latency[f'processed_combine_chunk_{i}-{select_chunks_upto}'] = f'{processing_chunks_elapsed_end_time:.2f}'
          uri_latency[f'processed_chunk_detail_{i}-{select_chunks_upto}'] = latency_processed_chunk
          # 📊 STEP 12: Update Progress
          end_time = datetime.now()
          processed_time = end_time - start_time
          
          process_logger.log_step(
            f"BATCH_{i//update_graph_chunk_processed + 1}_PROGRESS_UPDATE",
            f"Updating progress after batch {i//update_graph_chunk_processed + 1}",
            {
              'batch_completed': i//update_graph_chunk_processed + 1,
              'chunks_processed': select_chunks_upto + select_chunks_with_retry,
              'total_chunks': total_chunks,
              'current_node_count': node_count,
              'current_rel_count': rel_count,
              'elapsed_time': str(processed_time)
            }
          )
          
          obj_source_node = sourceNode()
          obj_source_node.file_name = file_name
          obj_source_node.updated_at = end_time
          obj_source_node.processing_time = processed_time
          obj_source_node.processed_chunk = select_chunks_upto+select_chunks_with_retry
          if retry_condition == START_FROM_BEGINNING:
            result = execute_graph_query(graph,QUERY_TO_GET_NODES_AND_RELATIONS_OF_A_DOCUMENT, params={"filename":file_name})
            obj_source_node.node_count = result[0]['nodes']
            obj_source_node.relationship_count = result[0]['rels']
          else:  
            obj_source_node.node_count = node_count
            obj_source_node.relationship_count = rel_count
          graphDb_data_Access.update_source_node(obj_source_node)
          graphDb_data_Access.update_node_relationship_count(file_name)
      
      # 🏁 STEP 13: Final Status Check and Cleanup
      result = graphDb_data_Access.get_current_status_document_node(file_name)
      is_cancelled_status = result[0]['is_cancelled']
      if bool(is_cancelled_status) == True:
        job_status = 'Cancelled'
        
        process_logger.log_step(
          "FINAL_STATUS_CANCELLED",
          "Final status check: Processing was cancelled",
          {
            'final_status': 'Cancelled',
            'cancellation_point': 'final_check',
            'chunks_processed': select_chunks_upto + select_chunks_with_retry if 'select_chunks_upto' in locals() else 0
          },
          level="WARNING"
        )
        
        logging.info(f'Is_cancelled True at the end extraction')
        
      process_logger.log_step(
        "PROCESSING_FINALIZATION",
        f"Finalizing processing with status: {job_status}",
        {
          'final_status': job_status,
          'total_processing_time': str(processed_time),
          'final_node_count': node_count,
          'final_rel_count': rel_count
        }
      )
      
      logging.info(f'Job Status at the end : {job_status}')
      end_time = datetime.now()
      processed_time = end_time - start_time
      
      # 💾 STEP 14: Final Database Update
      obj_source_node = sourceNode()
      obj_source_node.file_name = file_name.strip() if isinstance(file_name, str) else file_name
      obj_source_node.status = job_status
      obj_source_node.processing_time = processed_time

      graphDb_data_Access.update_source_node(obj_source_node)
      graphDb_data_Access.update_node_relationship_count(file_name)
      
      process_logger.log_step(
        "FINAL_DB_UPDATE",
        "Final database update completed",
        {
          'final_status': job_status,
          'total_processing_time': str(processed_time),
          'node_count': node_count,
          'relationship_count': rel_count,
          'update_completed': True
        }
      )
      
      logging.info('Updated the nodeCount and relCount properties in Document node')
      logging.info(f'file:{file_name} extraction has been completed')


      # 🗑️ STEP 15: File Cleanup
      if is_uploaded_from_local:
        gcs_file_cache = os.environ.get('GCS_FILE_CACHE')
        
        process_logger.log_step(
          "FILE_CLEANUP_START",
          "Starting file cleanup process",
          {
            'is_uploaded_from_local': is_uploaded_from_local,
            'gcs_file_cache': gcs_file_cache,
            'file_name': file_name,
            'merged_file_path': merged_file_path
          }
        )
        
        if gcs_file_cache == 'True':
          folder_name = create_gcs_bucket_folder_name_hashed(uri, file_name)
          delete_file_from_gcs(BUCKET_UPLOAD,folder_name,file_name)
          
          process_logger.log_step(
            "GCS_FILE_DELETED",
            "File deleted from GCS bucket",
            {
              'bucket': BUCKET_UPLOAD,
              'folder_name': folder_name,
              'file_name': file_name
            }
          )
        else:
          delete_uploaded_local_file(merged_file_path, file_name)
          
          process_logger.log_step(
            "LOCAL_FILE_DELETED",
            "File deleted from local storage",
            {
              'merged_file_path': merged_file_path,
              'file_name': file_name
            }
          )
      
      # 📈 STEP 16: Performance Metrics Calculation
      processing_source_func = time.time() - processing_source_start_time
      logging.info(f"Time taken to processing source function completed in {processing_source_func:.2f} seconds for file name {file_name}")  
      uri_latency["Processed_source"] = f'{processing_source_func:.2f}'
      if node_count == 0:
        uri_latency["Per_entity_latency"] = 'N/A'
      else:  
        uri_latency["Per_entity_latency"] = f'{int(processing_source_func)/node_count}/s'
      
      # 📊 STEP 17: Final Response Preparation
      response["fileName"] = file_name
      response["nodeCount"] = node_count
      response["relationshipCount"] = rel_count
      response["total_processing_time"] = round(processed_time.total_seconds(),2)
      response["status"] = job_status
      response["model"] = model
      response["success_count"] = 1
      
      # 🏁 STEP 18: Complete Process Logging with Enhanced Analytics
      final_stats = process_logger.end_process(
        job_status,
        {
          'file_name': file_name,
          'node_count': node_count,
          'relationship_count': rel_count,
          'total_processing_time': round(processed_time.total_seconds(),2),
          'model': model,
          'uri_latency': uri_latency,
          'response': response,
          'chunks_processed': select_chunks_upto + select_chunks_with_retry if 'select_chunks_upto' in locals() else 0,
          'processing_efficiency': {
            'nodes_per_second': node_count / processed_time.total_seconds() if processed_time.total_seconds() > 0 else 0,
            'relationships_per_second': rel_count / processed_time.total_seconds() if processed_time.total_seconds() > 0 else 0,
            'chunks_per_second': (select_chunks_upto + select_chunks_with_retry) / processed_time.total_seconds() if 'select_chunks_upto' in locals() and processed_time.total_seconds() > 0 else 0
          }
        }
      )
      
      # Log custom metrics for analysis
      process_logger.log_custom_metric("nodes_created", node_count, "DOCUMENT_PROCESSING", {"model": model})
      process_logger.log_custom_metric("relationships_created", rel_count, "DOCUMENT_PROCESSING", {"model": model})
      process_logger.log_custom_metric("processing_duration", processed_time.total_seconds(), "DOCUMENT_PROCESSING", {"model": model})
      
      # Log performance insights
      insights = process_logger.get_process_insights()
      logging.info(f"📊 Process insights: {json.dumps(insights, indent=2)}")
      
      return uri_latency, response
    else:
      process_logger.log_step(
        "DOCUMENT_ALREADY_PROCESSING",
        "Document is already being processed",
        {
          'file_name': file_name,
          'current_status': result[0]['Status'],
          'reason': 'document_already_in_processing_state'
        },
        level="WARNING"
      )
      
      logging.info("File does not process because its already in Processing status")
      return uri_latency,response
  else:
    error_message = "Unable to get the status of document node."
    
    process_logger.log_step(
      "DOCUMENT_STATUS_ERROR",
      "Failed to retrieve document status",
      {
        'file_name': file_name,
        'error': error_message,
        'result_length': len(result)
      },
      level="ERROR"
    )
    
    logging.error(error_message)
    raise LLMGraphBuilderException(error_message)

async def processing_chunks(chunkId_chunkDoc_list,graph,uri, userName, password, database,file_name,model,allowedNodes,allowedRelationship, chunks_to_combine, node_count, rel_count, additional_instructions=None):
  """
  Process chunks through LLM for entity extraction and relationship creation
  """
  # 🔄 STEP A: Initialize Chunk Processing
  process_logger.log_step(
    "CHUNK_PROCESSING_START",
    "Starting chunk processing for entity extraction",
    {
      'chunk_count': len(chunkId_chunkDoc_list),
      'file_name': file_name,
      'model': model,
      'chunks_to_combine': chunks_to_combine,
      'allowed_nodes': allowedNodes,
      'allowed_relationships': allowedRelationship,
      'current_node_count': node_count,
      'current_rel_count': rel_count
    }
  )
  
  latency_processing_chunk = {}
  
  # 🔗 STEP B: Database Connection Check
  if graph is not None:
    if graph._driver._closed:
      process_logger.log_step(
        "DB_RECONNECTION",
        "Database connection was closed, reconnecting",
        {
          'reconnection_reason': 'closed_connection',
          'uri': uri,
          'database': database
        }
      )
      graph = create_graph_database_connection(uri, userName, password, database)
  else:
    process_logger.log_step(
      "DB_CONNECTION_INIT",
      "Initializing database connection for chunk processing",
      {
        'uri': uri,
        'database': database
      }
    )
    graph = create_graph_database_connection(uri, userName, password, database)
  
  # 🔍 STEP C: Embedding Creation
  process_logger.log_step(
    "EMBEDDING_CREATION_START",
    "Creating embeddings for chunks",
    {
      'chunk_count': len(chunkId_chunkDoc_list),
      'file_name': file_name,
      'embedding_model': 'BAAI/bge-m3'
    }
  )
  
  start_update_embedding = time.time()
  create_chunk_embeddings( graph, chunkId_chunkDoc_list, file_name)
  end_update_embedding = time.time()
  elapsed_update_embedding = end_update_embedding - start_update_embedding
  
  process_logger.log_step(
    "EMBEDDING_CREATION_COMPLETE",
    "Chunk embeddings created successfully",
    {
      'embedding_time': f'{elapsed_update_embedding:.2f}s',
      'chunks_processed': len(chunkId_chunkDoc_list),
      'avg_time_per_chunk': f'{elapsed_update_embedding/len(chunkId_chunkDoc_list):.3f}s'
    }
  )
  
  logging.info(f'Time taken to update embedding in chunk node: {elapsed_update_embedding:.2f} seconds')
  latency_processing_chunk["update_embedding"] = f'{elapsed_update_embedding:.2f}'
  
  # 🤖 STEP D: LLM Entity Extraction
  process_logger.log_step(
    "ENTITY_EXTRACTION_START",
    "Starting entity extraction using LLM",
    {
      'model': model,
      'chunk_count': len(chunkId_chunkDoc_list),
      'chunks_to_combine': chunks_to_combine,
      'allowed_nodes': allowedNodes,
      'allowed_relationships': allowedRelationship,
      'additional_instructions': additional_instructions is not None
    }
  )
  
  logging.info("Get graph document list from models")
  
  start_entity_extraction = time.time()
  graph_documents =  await get_graph_from_llm(model, chunkId_chunkDoc_list, allowedNodes, allowedRelationship, chunks_to_combine, additional_instructions)
  end_entity_extraction = time.time()
  elapsed_entity_extraction = end_entity_extraction - start_entity_extraction
  
  # Check for performance bottlenecks
  if elapsed_entity_extraction > 60:  # More than 1 minute
    process_logger.log_performance_bottleneck(
      "ENTITY_EXTRACTION", 
      "SLOW_LLM_PROCESSING",
      {
        'processing_time': elapsed_entity_extraction,
        'chunk_count': len(chunkId_chunkDoc_list),
        'model': model,
        'threshold': 60,
        'avg_time_per_chunk': elapsed_entity_extraction / len(chunkId_chunkDoc_list)
      }
    )
  
  process_logger.log_data_flow(
    "ENTITY_EXTRACTION_COMPLETE",
    {
      'input_chunks': len(chunkId_chunkDoc_list),
      'model': model,
      'chunks_to_combine': chunks_to_combine
    },
    {
      'graph_documents': len(graph_documents),
      'entities_extracted': sum(len(doc.nodes) for doc in graph_documents),
      'relationships_extracted': sum(len(doc.relationships) for doc in graph_documents)
    },
    elapsed_entity_extraction,
    {
      'extraction_quality': 'high' if graph_documents else 'low',
      'avg_entities_per_chunk': sum(len(doc.nodes) for doc in graph_documents) / len(chunkId_chunkDoc_list) if chunkId_chunkDoc_list else 0,
      'avg_relationships_per_chunk': sum(len(doc.relationships) for doc in graph_documents) / len(chunkId_chunkDoc_list) if chunkId_chunkDoc_list else 0
    }
  )
  
  logging.info(f'Time taken to extract enitities from LLM Graph Builder: {elapsed_entity_extraction:.2f} seconds')
  latency_processing_chunk["entity_extraction"] = f'{elapsed_entity_extraction:.2f}'
  
  # 🧹 STEP E: Data Cleaning
  process_logger.log_step(
    "DATA_CLEANING_START",
    "Cleaning extracted graph documents",
    {
      'raw_graph_documents': len(graph_documents),
      'cleaning_process': 'handle_backticks_nodes_relationship_id_type'
    }
  )
  
  cleaned_graph_documents = handle_backticks_nodes_relationship_id_type(graph_documents)
  
  process_logger.log_step(
    "DATA_CLEANING_COMPLETE",
    "Graph documents cleaned successfully",
    {
      'cleaned_graph_documents': len(cleaned_graph_documents),
      'cleaning_applied': 'backticks_and_id_type_normalization'
    }
  )
  
  # 💾 STEP F: Save to Neo4j
  process_logger.log_step(
    "NEO4J_SAVE_START",
    "Saving graph documents to Neo4j database",
    {
      'documents_to_save': len(cleaned_graph_documents),
      'total_nodes': sum(len(doc.nodes) for doc in cleaned_graph_documents),
      'total_relationships': sum(len(doc.relationships) for doc in cleaned_graph_documents)
    }
  )
  
  start_save_graphDocuments = time.time()
  save_graphDocuments_in_neo4j(graph, cleaned_graph_documents)
  end_save_graphDocuments = time.time()
  elapsed_save_graphDocuments = end_save_graphDocuments - start_save_graphDocuments
  
  process_logger.log_step(
    "NEO4J_SAVE_COMPLETE",
    "Graph documents saved to Neo4j successfully",
    {
      'save_time': f'{elapsed_save_graphDocuments:.2f}s',
      'documents_saved': len(cleaned_graph_documents),
      'avg_time_per_document': f'{elapsed_save_graphDocuments/len(cleaned_graph_documents):.3f}s'
    }
  )
  
  logging.info(f'Time taken to save graph document in neo4j: {elapsed_save_graphDocuments:.2f} seconds')
  latency_processing_chunk["save_graphDocuments"] = f'{elapsed_save_graphDocuments:.2f}'

  # 🔗 STEP G: Chunk-Entity Relationship Creation
  process_logger.log_step(
    "CHUNK_ENTITY_MAPPING_START",
    "Creating chunk-entity mapping",
    {
      'graph_documents': len(cleaned_graph_documents),
      'chunk_documents': len(chunkId_chunkDoc_list),
      'mapping_purpose': 'link_chunks_to_extracted_entities'
    }
  )
  
  chunks_and_graphDocuments_list = get_chunk_and_graphDocument(cleaned_graph_documents, chunkId_chunkDoc_list)
  
  process_logger.log_step(
    "CHUNK_ENTITY_RELATIONSHIP_START",
    "Creating relationships between chunks and entities",
    {
      'chunk_entity_pairs': len(chunks_and_graphDocuments_list),
      'relationship_type': 'HAS_ENTITY'
    }
  )

  start_relationship = time.time()
  merge_relationship_between_chunk_and_entites(graph, chunks_and_graphDocuments_list)
  end_relationship = time.time()
  elapsed_relationship = end_relationship - start_relationship
  
  process_logger.log_step(
    "CHUNK_ENTITY_RELATIONSHIP_COMPLETE",
    "Chunk-entity relationships created successfully",
    {
      'relationship_time': f'{elapsed_relationship:.2f}s',
      'relationships_created': len(chunks_and_graphDocuments_list),
      'relationship_type': 'HAS_ENTITY'
    }
  )
  
  logging.info(f'Time taken to create relationship between chunk and entities: {elapsed_relationship:.2f} seconds')
  latency_processing_chunk["relationship_between_chunk_entity"] = f'{elapsed_relationship:.2f}'
  
  # 📊 STEP H: Count Updates
  process_logger.log_step(
    "COUNT_UPDATE_START",
    "Updating node and relationship counts",
    {
      'file_name': file_name,
      'purpose': 'update_document_statistics'
    }
  )
  
  graphDb_data_Access = graphDBdataAccess(graph)
  count_response = graphDb_data_Access.update_node_relationship_count(file_name)
  node_count = count_response[file_name].get('nodeCount',"0")
  rel_count = count_response[file_name].get('relationshipCount',"0")
  
  process_logger.log_step(
    "CHUNK_PROCESSING_COMPLETE",
    "Chunk processing completed successfully",
    {
      'final_node_count': node_count,
      'final_rel_count': rel_count,
      'chunks_processed': len(chunkId_chunkDoc_list),
      'latency_breakdown': latency_processing_chunk
    }
  )
  
  return node_count,rel_count,latency_processing_chunk

def get_chunkId_chunkDoc_list(graph, file_name, pages, token_chunk_size, chunk_overlap, retry_condition):
  if not retry_condition:
    logging.info("Break down file into chunks")
    bad_chars = ['"', "\n", "'"]
    for i in range(0,len(pages)):
      text = pages[i].page_content
      for j in bad_chars:
        if j == '\n':
          text = text.replace(j, ' ')
        else:
          text = text.replace(j, '')
      pages[i]=Document(page_content=str(text), metadata=pages[i].metadata)
    create_chunks_obj = CreateChunksofDocument(pages, graph)
    chunks = create_chunks_obj.split_file_into_chunks(token_chunk_size, chunk_overlap)
    chunkId_chunkDoc_list = create_relation_between_chunks(graph,file_name,chunks)
    return len(chunks), chunkId_chunkDoc_list
  
  else:  
    chunkId_chunkDoc_list=[]
    chunks =  execute_graph_query(graph,QUERY_TO_GET_CHUNKS, params={"filename":file_name})
    
    if chunks[0]['text'] is None or chunks[0]['text']=="" or not chunks :
      raise LLMGraphBuilderException(f"Chunks are not created for {file_name}. Please re-upload file and try again.")    
    else:
      for chunk in chunks:
        chunk_doc = Document(page_content=chunk['text'], metadata={'id':chunk['id'], 'position':chunk['position']})
        chunkId_chunkDoc_list.append({'chunk_id': chunk['id'], 'chunk_doc': chunk_doc})
      
      if retry_condition ==  START_FROM_LAST_PROCESSED_POSITION:
        logging.info(f"Retry : start_from_last_processed_position")
        starting_chunk = execute_graph_query(graph,QUERY_TO_GET_LAST_PROCESSED_CHUNK_POSITION, params={"filename":file_name})
        
        if starting_chunk and starting_chunk[0]["position"] < len(chunkId_chunkDoc_list):
          return len(chunks), chunkId_chunkDoc_list[starting_chunk[0]["position"] - 1:]
        
        elif starting_chunk and starting_chunk[0]["position"] == len(chunkId_chunkDoc_list):
          starting_chunk =  execute_graph_query(graph,QUERY_TO_GET_LAST_PROCESSED_CHUNK_WITHOUT_ENTITY, params={"filename":file_name})
          return len(chunks), chunkId_chunkDoc_list[starting_chunk[0]["position"] - 1:]
        
        else:
          raise LLMGraphBuilderException(f"All chunks of file {file_name} are already processed. If you want to re-process, Please start from begnning")    
      
      else:
        logging.info(f"Retry : start_from_beginning with chunks {len(chunkId_chunkDoc_list)}")    
        return len(chunks), chunkId_chunkDoc_list
  
def get_source_list_from_graph(uri,userName,password,db_name=None):
  """
  Args:
    uri: URI of the graph to extract
    db_name: db_name is database name to connect to graph db
    userName: Username to use for graph creation ( if None will use username from config file )
    password: Password to use for graph creation ( if None will use password from config file )
    file: File object containing the PDF file to be used
    model: Type of model to use ('Diffbot'or'OpenAI GPT')
  Returns:
   Returns a list of sources that are in the database by querying the graph and
   sorting the list by the last updated date. 
 """
  logging.info("Get existing files list from graph")
  graph = Neo4jGraph(url=uri, database=db_name, username=userName, password=password)
  graph_DB_dataAccess = graphDBdataAccess(graph)
  if not graph._driver._closed:
      logging.info(f"closing connection for sources_list api")
      graph._driver.close()
  return graph_DB_dataAccess.get_source_list()

def update_graph(graph):
  """
  Update the graph node with SIMILAR relationship where embedding scrore match
  """
  graph_DB_dataAccess = graphDBdataAccess(graph)
  graph_DB_dataAccess.update_KNN_graph()

  
def connection_check_and_get_vector_dimensions(graph,database):
  """
  Args:
    uri: URI of the graph to extract
    userName: Username to use for graph creation ( if None will use username from config file )
    password: Password to use for graph creation ( if None will use password from config file )
    db_name: db_name is database name to connect to graph db
  Returns:
   Returns a status of connection from NEO4j is success or failure
 """
  graph_DB_dataAccess = graphDBdataAccess(graph)
  return graph_DB_dataAccess.connection_check_and_get_vector_dimensions(database)

def merge_chunks_local(file_name, total_chunks, chunk_dir, merged_dir):

  if not os.path.exists(merged_dir):
      os.mkdir(merged_dir)
  logging.info(f'Merged File Path: {merged_dir}')
  merged_file_path = os.path.join(merged_dir, file_name)
  with open(merged_file_path, "wb") as write_stream:
      for i in range(1,total_chunks+1):
          chunk_file_path = os.path.join(chunk_dir, f"{file_name}_part_{i}")
          logging.info(f'Chunk File Path While Merging Parts:{chunk_file_path}')
          with open(chunk_file_path, "rb") as chunk_file:
              shutil.copyfileobj(chunk_file, write_stream)
          os.unlink(chunk_file_path)  # Delete the individual chunk file after merging
  logging.info("Chunks merged successfully and return file size")
  
  file_size = os.path.getsize(merged_file_path)
  return file_size
  


def upload_file(graph, model, chunk, chunk_number:int, total_chunks:int, originalname, uri, chunk_dir, merged_dir):
  
  gcs_file_cache = os.environ.get('GCS_FILE_CACHE')
  logging.info(f'gcs file cache: {gcs_file_cache}')
  
  if gcs_file_cache == 'True':
    folder_name = create_gcs_bucket_folder_name_hashed(uri,originalname)
    upload_file_to_gcs(chunk, chunk_number, originalname, BUCKET_UPLOAD, folder_name)
  else:
    if not os.path.exists(chunk_dir):
      os.mkdir(chunk_dir)
    
    chunk_file_path = os.path.join(chunk_dir, f"{originalname}_part_{chunk_number}")
    logging.info(f'Chunk File Path: {chunk_file_path}')
    
    with open(chunk_file_path, "wb") as chunk_file:
      chunk_file.write(chunk.file.read())

  if int(chunk_number) == int(total_chunks):
      # If this is the last chunk, merge all chunks into a single file
      if gcs_file_cache == 'True':
        file_size = merge_file_gcs(BUCKET_UPLOAD, originalname, folder_name, int(total_chunks))
      else:
        file_size = merge_chunks_local(originalname, int(total_chunks), chunk_dir, merged_dir)
      
      logging.info("File merged successfully")
      file_extension = originalname.split('.')[-1]
      obj_source_node = sourceNode()
      obj_source_node.file_name = originalname.strip() if isinstance(originalname, str) else originalname
      obj_source_node.file_type = file_extension
      obj_source_node.file_size = file_size
      obj_source_node.file_source = 'local file'
      obj_source_node.model = model
      obj_source_node.created_at = datetime.now()
      obj_source_node.chunkNodeCount=0
      obj_source_node.chunkRelCount=0
      obj_source_node.entityNodeCount=0
      obj_source_node.entityEntityRelCount=0
      obj_source_node.communityNodeCount=0
      obj_source_node.communityRelCount=0
      graphDb_data_Access = graphDBdataAccess(graph)
        
      graphDb_data_Access.create_source_node(obj_source_node)
      return {'file_size': file_size, 'file_name': originalname, 'file_extension':file_extension, 'message':f"Chunk {chunk_number}/{total_chunks} saved"}
  return f"Chunk {chunk_number}/{total_chunks} saved"

def get_labels_and_relationtypes(uri, userName, password, database):
  excluded_labels = {'Document', 'Chunk', '_Bloom_Perspective_', '__Community__', '__Entity__', 'Session', 'Message'}
  excluded_relationships = {
       'NEXT_CHUNK', '_Bloom_Perspective_', 'FIRST_CHUNK',
       'SIMILAR', 'IN_COMMUNITY', 'PARENT_COMMUNITY', 'NEXT', 'LAST_MESSAGE',
       'PART_OF', 'HAS_ENTITY'  # Add missing system relationships
   }
  driver = get_graphDB_driver(uri, userName, password,database) 
  triples = set()
  with driver.session(database=database) as session:
    result = session.run("""
           MATCH (n)-[r]->(m)
           RETURN DISTINCT labels(n) AS fromLabels, type(r) AS relType, labels(m) AS toLabels
       """)
    for record in result:
      from_labels = record["fromLabels"]
      to_labels = record["toLabels"]
      rel_type = record["relType"]
      from_label = next((lbl for lbl in from_labels if lbl not in excluded_labels), None)
      to_label = next((lbl for lbl in to_labels if lbl not in excluded_labels), None)
      if not from_label or not to_label:
          continue
      if rel_type == 'PART_OF':
          if from_label == 'Chunk' and to_label == 'Document':
              continue 
      elif rel_type == 'HAS_ENTITY':
          if from_label == 'Chunk':
              continue 
      elif (
          from_label in excluded_labels or
          to_label in excluded_labels or
          rel_type in excluded_relationships
      ):
          continue
      triples.add(f"{from_label}-{rel_type}->{to_label}")
  return {"triplets": list(triples)}

def manually_cancelled_job(graph, filenames, source_types, merged_dir, uri):
  
  filename_list= list(map(str.strip, json.loads(filenames)))
  source_types_list= list(map(str.strip, json.loads(source_types)))
  gcs_file_cache = os.environ.get('GCS_FILE_CACHE')
  
  for (file_name,source_type) in zip(filename_list, source_types_list):
      obj_source_node = sourceNode()
      obj_source_node.file_name = file_name.strip() if isinstance(file_name, str) else file_name
      obj_source_node.is_cancelled = True
      obj_source_node.status = 'Cancelled'
      obj_source_node.updated_at = datetime.now()
      graphDb_data_Access = graphDBdataAccess(graph)
      graphDb_data_Access.update_source_node(obj_source_node)
      count_response = graphDb_data_Access.update_node_relationship_count(file_name)
      obj_source_node = None
      merged_file_path = os.path.join(merged_dir, file_name)
      if source_type == 'local file' and gcs_file_cache == 'True':
          folder_name = create_gcs_bucket_folder_name_hashed(uri, file_name)
          delete_file_from_gcs(BUCKET_UPLOAD,folder_name,file_name)
      else:
        logging.info(f'Deleted File Path: {merged_file_path} and Deleted File Name : {file_name}')
        delete_uploaded_local_file(merged_file_path,file_name)
  return "Cancelled the processing job successfully"

def populate_graph_schema_from_text(text, model, is_schema_description_checked, is_local_storage):
  """_summary_

  Args:
      graph (Neo4Graph): Neo4jGraph connection object
      input_text (str): rendom text from PDF or user input.
      model (str): AI model to use extraction from text

  Returns:
      data (list): list of lebels and relationTypes
  """
  result = schema_extraction_from_text(text, model, is_schema_description_checked, is_local_storage)
  return result

def set_status_retry(graph, file_name, retry_condition):
    graphDb_data_Access = graphDBdataAccess(graph)
    obj_source_node = sourceNode()
    status = "Ready to Reprocess"
    obj_source_node.file_name = file_name.strip() if isinstance(file_name, str) else file_name
    obj_source_node.status = status
    obj_source_node.retry_condition = retry_condition
    obj_source_node.is_cancelled = False
    if retry_condition == DELETE_ENTITIES_AND_START_FROM_BEGINNING or retry_condition == START_FROM_BEGINNING:
        obj_source_node.processed_chunk=0
    if retry_condition == DELETE_ENTITIES_AND_START_FROM_BEGINNING:
        execute_graph_query(graph,QUERY_TO_DELETE_EXISTING_ENTITIES, params={"filename":file_name})
        obj_source_node.node_count=0
        obj_source_node.relationship_count=0
    logging.info(obj_source_node)
    graphDb_data_Access.update_source_node(obj_source_node)

def failed_file_process(uri,file_name, merged_file_path):
  gcs_file_cache = os.environ.get('GCS_FILE_CACHE')
  if gcs_file_cache == 'True':
      folder_name = create_gcs_bucket_folder_name_hashed(uri,file_name)
      copy_failed_file(BUCKET_UPLOAD, BUCKET_FAILED_FILE, folder_name, file_name)
      time.sleep(5)
      delete_file_from_gcs(BUCKET_UPLOAD,folder_name,file_name)
  else:
      logging.info(f'Deleted File Path: {merged_file_path} and Deleted File Name : {file_name}')
      delete_uploaded_local_file(merged_file_path,file_name)