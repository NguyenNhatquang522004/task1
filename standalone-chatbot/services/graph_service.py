"""
Graph Query Service
"""
import logging
from typing import Dict, Any
from langchain_neo4j import GraphCypherQAChain
from models.chat_models import get_llm

logger = logging.getLogger(__name__)

class GraphQueryService:
    """Handles graph-based queries using Cypher"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def create_graph_chain(self, model: str):
        """Create GraphCypherQAChain"""
        try:
            logger.info(f"Graph QA Chain using LLM model: {model}")
            
            cypher_llm, model_name = get_llm(model)
            qa_llm, _ = get_llm(model)
            
            graph_chain = GraphCypherQAChain.from_llm(
                cypher_llm=cypher_llm,
                qa_llm=qa_llm,
                validate_cypher=True,
                graph=self.graph,
                allow_dangerous_requests=True,
                return_intermediate_steps=True,
                top_k=3
            )
            
            logger.info("GraphCypherQAChain instance created successfully.")
            return graph_chain, qa_llm, model_name
            
        except Exception as e:
            logger.error(f"An error occurred while creating the GraphCypherQAChain instance: {e}")
            raise
    
    def get_graph_response(self, graph_chain, question: str) -> Dict[str, Any]:
        """Execute graph query and return response"""
        try:
            cypher_res = graph_chain.invoke({"query": question})
            
            response = cypher_res.get("result")
            cypher_query = ""
            context = []
            
            for step in cypher_res.get("intermediate_steps", []):
                if "query" in step:
                    cypher_string = step["query"]
                    cypher_query = cypher_string.replace("cypher\n", "").replace("\n", " ").strip()
                elif "context" in step:
                    context = step["context"]
                    
            return {
                "response": response,
                "cypher_query": cypher_query,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"An error occurred while getting the graph response: {e}")
            raise
    
    def query_graph(self, question: str, model: str) -> Dict[str, Any]:
        """Execute graph query and return structured response"""
        try:
            graph_chain, qa_llm, model_version = self.create_graph_chain(model)
            graph_response = self.get_graph_response(graph_chain, question)
            
            ai_response_content = graph_response.get("response", "Something went wrong")
            
            result = {
                "message": ai_response_content,
                "model": model_version,
                "cypher_query": graph_response.get("cypher_query", ""),
                "context": graph_response.get("context", ""),
                "mode": "graph"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing graph response: {e}")
            return {
                "message": "Something went wrong with the graph query",
                "model": model,
                "cypher_query": "",
                "context": "",
                "mode": "graph",
                "error": str(e)
            }
