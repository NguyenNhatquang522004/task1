"""
Integration module for connecting cross-document analysis with main LLM Graph Builder
"""

import logging
from typing import Optional
from fastapi import FastAPI

from .src.api.routes import router
from .src.core.analyzer import CrossDocumentAnalyzer
from .src.utils.helpers import setup_logging
from .config.settings import config

logger = logging.getLogger(__name__)

class CrossDocumentIntegration:
    """Integration class for cross-document functionality"""
    
    def __init__(self):
        self.analyzer: Optional[CrossDocumentAnalyzer] = None
        self.neo4j_driver = None
        self.llm_client = None
        
    def initialize(self, llm_client=None, neo4j_driver=None, use_gemini=True):
        """
        Initialize the cross-document analysis with dependencies
        
        Args:
            llm_client: LLM client instance from main application (optional if use_gemini=True)
            neo4j_driver: Neo4j driver instance from main application
            use_gemini: Whether to use Gemini 2.0 Flash with API key rotation
        """
        try:
            self.llm_client = llm_client
            self.neo4j_driver = neo4j_driver
            
            # Create analyzer instance with Gemini support
            self.analyzer = CrossDocumentAnalyzer(
                llm_client=llm_client,
                neo4j_driver=neo4j_driver,
                similarity_threshold=config.DEFAULT_SIMILARITY_THRESHOLD,
                use_gemini=use_gemini
            )
            
            if use_gemini:
                logger.info("Cross-document analysis initialized with Gemini 2.0 Flash and API key rotation")
                
                # Log Gemini status
                try:
                    status = self.analyzer.get_llm_status()
                    logger.info(f"Gemini client status: {status}")
                except Exception as e:
                    logger.warning(f"Could not get Gemini status: {str(e)}")
            else:
                logger.info("Cross-document analysis initialized with provided LLM client")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize cross-document analysis: {str(e)}")
            return False
    
    def setup_dependencies(self):
        """Setup FastAPI dependencies for the routes"""
        
        def get_analyzer_dependency():
            if not self.analyzer:
                raise RuntimeError("Cross-document analyzer not initialized")
            return self.analyzer
            
        def get_neo4j_driver_dependency():
            if not self.neo4j_driver:
                raise RuntimeError("Neo4j driver not initialized")
            return self.neo4j_driver
        
        # Update the dependency functions in routes
        import sys
        routes_module = sys.modules.get('cross-document-relationships.src.api.routes')
        if routes_module:
            routes_module.get_analyzer = get_analyzer_dependency
            routes_module.get_neo4j_driver = get_neo4j_driver_dependency
    
    def add_routes_to_app(self, app: FastAPI):
        """
        Add cross-document routes to the main FastAPI application
        
        Args:
            app: FastAPI application instance
        """
        try:
            # Setup dependencies
            self.setup_dependencies()
            
            # Include router
            app.include_router(router)
            
            logger.info("Cross-document routes added to FastAPI application")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add cross-document routes: {str(e)}")
            return False
    
    def health_check(self) -> dict:
        """
        Perform health check for cross-document functionality
        
        Returns:
            Health status dictionary
        """
        status = {
            "service": "cross-document-relationships",
            "status": "healthy",
            "components": {}
        }
        
        try:
            # Check analyzer
            if self.analyzer:
                status["components"]["analyzer"] = "initialized"
            else:
                status["components"]["analyzer"] = "not_initialized"
                status["status"] = "unhealthy"
            
            # Check Neo4j connection
            if self.neo4j_driver:
                try:
                    with self.neo4j_driver.session() as session:
                        session.run("RETURN 1")
                    status["components"]["neo4j"] = "connected"
                except Exception:
                    status["components"]["neo4j"] = "connection_error"
                    status["status"] = "unhealthy"
            else:
                status["components"]["neo4j"] = "not_initialized"
                status["status"] = "unhealthy"
            
            # Check LLM client (Gemini or other)
            if self.analyzer:
                try:
                    llm_status = self.analyzer.get_llm_status()
                    status["components"]["llm_client"] = {
                        "status": "initialized",
                        "details": llm_status
                    }
                except Exception as e:
                    status["components"]["llm_client"] = {
                        "status": "error",
                        "error": str(e)
                    }
                    status["status"] = "degraded"
            else:
                status["components"]["llm_client"] = "not_initialized"
                status["status"] = "unhealthy"
                
        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)
            
        return status

# Global integration instance
integration = CrossDocumentIntegration()

def setup_cross_document_analysis(app: FastAPI, llm_client=None, neo4j_driver=None, use_gemini=True):
    """
    Setup cross-document analysis for the main application
    
    Args:
        app: FastAPI application
        llm_client: LLM client instance (optional if use_gemini=True)
        neo4j_driver: Neo4j driver instance
        use_gemini: Whether to use Gemini 2.0 Flash with API key rotation
        
    Returns:
        True if setup successful, False otherwise
    """
    try:
        # Setup logging
        setup_logging(config.LOG_LEVEL)
        
        # Initialize integration with Gemini support
        if not integration.initialize(llm_client, neo4j_driver, use_gemini):
            return False
            
        # Add routes to app
        if not integration.add_routes_to_app(app):
            return False
            
        logger.info("Cross-document analysis setup completed successfully")
        
        # Log configuration
        if use_gemini:
            logger.info(f"Using Gemini 2.0 Flash with {len(config.GEMINI_API_KEYS)} API keys")
        else:
            logger.info("Using provided LLM client")
            
        return True
        
    except Exception as e:
        logger.error(f"Cross-document analysis setup failed: {str(e)}")
        return False

def get_cross_document_analyzer() -> Optional[CrossDocumentAnalyzer]:
    """
    Get the cross-document analyzer instance
    
    Returns:
        Analyzer instance or None if not initialized
    """
    return integration.analyzer
