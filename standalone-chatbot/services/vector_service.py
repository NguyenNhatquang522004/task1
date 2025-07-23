"""
Vector Search Service
"""
import logging
from typing import List, Dict, Any, Optional
from langchain_neo4j import Neo4jVector
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter, DocumentCompressorPipeline
from langchain_text_splitters import TokenTextSplitter
from utils.embedding_utils import get_embedding_function
from config import CHAT_DOC_SPLIT_SIZE, CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD

logger = logging.getLogger(__name__)

class VectorSearchService:
    """Handles vector search operations"""
    
    def __init__(self, graph):
        self.graph = graph
        self.embedding_function, _ = get_embedding_function()
    
    def initialize_neo4j_vector(self, chat_mode_settings: Dict[str, Any]) -> Neo4jVector:
        """Initialize Neo4j vector index"""
        try:
            retrieval_query = chat_mode_settings.get("retrieval_query")
            index_name = chat_mode_settings.get("index_name")
            keyword_index = chat_mode_settings.get("keyword_index", "")
            node_label = chat_mode_settings.get("node_label")
            embedding_node_property = chat_mode_settings.get("embedding_node_property")
            text_node_properties = chat_mode_settings.get("text_node_properties")

            if not retrieval_query or not index_name:
                raise ValueError("Required settings 'retrieval_query' or 'index_name' are missing.")

            if keyword_index:
                neo_db = Neo4jVector.from_existing_graph(
                    embedding=self.embedding_function,
                    index_name=index_name,
                    retrieval_query=retrieval_query,
                    graph=self.graph,
                    search_type="hybrid",
                    node_label=node_label,
                    embedding_node_property=embedding_node_property,
                    text_node_properties=text_node_properties,
                    keyword_index_name=keyword_index
                )
                logger.info(f"Successfully retrieved Neo4jVector Fulltext index '{index_name}' and keyword index '{keyword_index}'")
            else:
                neo_db = Neo4jVector.from_existing_graph(
                    embedding=self.embedding_function,
                    index_name=index_name,
                    retrieval_query=retrieval_query,
                    graph=self.graph,
                    node_label=node_label,
                    embedding_node_property=embedding_node_property,
                    text_node_properties=text_node_properties
                )
                logger.info(f"Successfully retrieved Neo4jVector index '{index_name}'")
                
        except Exception as e:
            index_name = chat_mode_settings.get("index_name")
            logger.error(f"Error retrieving Neo4jVector index {index_name}: {e}")
            raise
            
        return neo_db
    
    def create_retriever(self, neo_db: Neo4jVector, document_names: Optional[List[str]], 
                        chat_mode_settings: Dict[str, Any], search_k: int, 
                        score_threshold: float, ef_ratio: int = 2):
        """Create document retriever"""
        try:
            if document_names and chat_mode_settings["document_filter"]:
                retriever = neo_db.as_retriever(
                    search_type="similarity_score_threshold",
                    search_kwargs={
                        'top_k': search_k,
                        'effective_search_ratio': ef_ratio,
                        'score_threshold': score_threshold,
                        'filter': {'fileName': {'$in': document_names}}
                    }
                )
                logger.info(f"Successfully created retriever with search_k={search_k}, score_threshold={score_threshold} for documents {document_names}")
            else:
                retriever = neo_db.as_retriever(
                    search_type="similarity_score_threshold",
                    search_kwargs={'top_k': search_k, 'effective_search_ratio': ef_ratio, 'score_threshold': score_threshold}
                )
                logger.info(f"Successfully created retriever with search_k={search_k}, score_threshold={score_threshold}")
                
            return retriever
            
        except Exception as e:
            logger.error(f"Error creating retriever: {e}")
            raise
    
    def get_neo4j_retriever(self, document_names: Optional[List[str]], 
                           chat_mode_settings: Dict[str, Any], 
                           score_threshold: float = 0.5):
        """Get Neo4j retriever with compression"""
        try:
            neo_db = self.initialize_neo4j_vector(chat_mode_settings)
            search_k = chat_mode_settings["top_k"]
            ef_ratio = 2  # Default effective search ratio
            
            base_retriever = self.create_retriever(neo_db, document_names, chat_mode_settings, search_k, score_threshold, ef_ratio)
            
            # Add compression pipeline
            splitter = TokenTextSplitter(chunk_size=CHAT_DOC_SPLIT_SIZE, chunk_overlap=0)
            embeddings_filter = EmbeddingsFilter(
                embeddings=self.embedding_function,
                similarity_threshold=CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD
            )
            
            pipeline_compressor = DocumentCompressorPipeline(
                transformers=[splitter, embeddings_filter]
            )
            
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=pipeline_compressor, 
                base_retriever=base_retriever
            )
            
            return compression_retriever
            
        except Exception as e:
            index_name = chat_mode_settings.get("index_name")
            logger.error(f"Error retrieving Neo4jVector index {index_name} or creating retriever: {e}")
            raise Exception(f"An error occurred while retrieving the Neo4jVector index or creating the retriever. Please drop and create a new vector index '{index_name}': {e}") from e
    
    def search_documents(self, query: str, document_names: Optional[List[str]], 
                        chat_mode_settings: Dict[str, Any]) -> List[Any]:
        """Search documents using vector similarity"""
        try:
            retriever = self.get_neo4j_retriever(document_names, chat_mode_settings)
            docs = retriever.invoke(query)
            logger.info(f"Retrieved {len(docs)} documents for query")
            return docs
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
