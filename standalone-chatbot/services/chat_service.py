"""
Chat Service - Core chat logic
"""
import time
import logging
from typing import List, Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from services.vector_service import VectorSearchService
from services.graph_service import GraphQueryService
from models.chat_models import get_llm
from config import CHAT_SYSTEM_TEMPLATE, QUESTION_TRANSFORM_TEMPLATE, CHAT_MODE_CONFIG_MAP, CHAT_TOKEN_CUT_OFF

logger = logging.getLogger(__name__)

class SessionChatHistory:
    """Manages chat history by session"""
    history_dict = {}

    @classmethod
    def get_chat_history(cls, session_id: str):
        """Retrieve or create chat message history for a given session ID"""
        if session_id not in cls.history_dict:
            logger.info(f"Creating new ChatMessageHistory for session ID: {session_id}")
            cls.history_dict[session_id] = ChatMessageHistory()
        else:
            logger.info(f"Retrieved existing ChatMessageHistory for session ID: {session_id}")
        return cls.history_dict[session_id]

class ChatService:
    """Main chat service handling both vector and graph queries"""
    
    def __init__(self, graph):
        self.graph = graph
        self.vector_service = VectorSearchService(graph)
        self.graph_service = GraphQueryService(graph)
    
    def get_chat_mode_settings(self, mode: str) -> Dict[str, Any]:
        """Get chat mode configuration"""
        try:
            default_settings = CHAT_MODE_CONFIG_MAP.get("vector", {})
            chat_mode_settings = CHAT_MODE_CONFIG_MAP.get(mode, default_settings)
            chat_mode_settings["mode"] = mode
            
            logger.info(f"Chat mode settings: {chat_mode_settings}")
            return chat_mode_settings
            
        except Exception as e:
            logger.error(f"Error getting chat mode settings: {e}")
            raise
    
    def create_document_retriever_chain(self, llm, retriever):
        """Create document retriever chain with query transformation"""
        try:
            logger.info("Starting to create document retriever chain")
            
            query_transform_prompt = ChatPromptTemplate.from_messages([
                ("system", QUESTION_TRANSFORM_TEMPLATE),
                MessagesPlaceholder(variable_name="messages")
            ])
            
            output_parser = StrOutputParser()
            
            query_transforming_retriever_chain = RunnableBranch(
                (
                    lambda x: len(x.get("messages", [])) == 1,
                    (lambda x: x["messages"][-1].content) | retriever,
                ),
                query_transform_prompt | llm | output_parser | retriever,
            ).with_config(run_name="chat_retriever_chain")
            
            logger.info("Successfully created document retriever chain")
            return query_transforming_retriever_chain
            
        except Exception as e:
            logger.error(f"Error creating document retriever chain: {e}")
            raise
    
    def get_rag_chain(self, llm, system_template: str = CHAT_SYSTEM_TEMPLATE):
        """Create RAG chain for question answering"""
        try:
            question_answering_prompt = ChatPromptTemplate.from_messages([
                ("system", system_template),
                MessagesPlaceholder(variable_name="messages"),
                ("human", "User question: {input}")
            ])
            
            question_answering_chain = question_answering_prompt | llm
            return question_answering_chain
            
        except Exception as e:
            logger.error(f"Error creating RAG chain: {e}")
            raise
    
    def format_documents(self, documents: List[Any], model: str, chat_mode_settings: Dict[str, Any]) -> str:
        """Format documents for context"""
        try:
            # Get token cutoff for model
            prompt_token_cutoff = 4
            for model_names, value in CHAT_TOKEN_CUT_OFF.items():
                if model in model_names:
                    prompt_token_cutoff = value
                    break
            
            # Sort by similarity score and limit
            sorted_documents = sorted(documents, key=lambda doc: doc.state.get("query_similarity_score", 0), reverse=True)
            sorted_documents = sorted_documents[:prompt_token_cutoff]
            
            formatted_docs = []
            sources = set()
            
            for doc in sorted_documents:
                try:
                    source = doc.metadata.get('source', "unknown")
                    sources.add(source)
                    
                    formatted_doc = (
                        "Document start\n"
                        f"This Document belongs to the source {source}\n"
                        f"Content: {doc.page_content}\n"
                        "Document end\n"
                    )
                    formatted_docs.append(formatted_doc)
                    
                except Exception as e:
                    logger.error(f"Error formatting document: {e}")
            
            return "\n\n".join(formatted_docs), list(sources)
            
        except Exception as e:
            logger.error(f"Error formatting documents: {e}")
            return "", []
    
    def retrieve_documents(self, doc_retriever, messages: List[Any]) -> List[Any]:
        """Retrieve documents using the retriever chain"""
        start_time = time.time()
        try:
            docs = doc_retriever.invoke({"messages": messages})
            doc_retrieval_time = time.time() - start_time
            logger.info(f"Documents retrieved in {doc_retrieval_time:.2f} seconds")
            return docs
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def process_vector_chat(self, question: str, model: str, document_names: Optional[List[str]], 
                           chat_mode_settings: Dict[str, Any], messages: List[Any]) -> Dict[str, Any]:
        """Process vector-based chat"""
        try:
            start_time = time.time()
            
            # Get LLM
            llm, model_name = get_llm(model)
            logger.info(f"Model called in chat: {model} (version: {model_name})")
            
            # Get retriever
            retriever = self.vector_service.get_neo4j_retriever(document_names, chat_mode_settings)
            doc_retriever = self.create_document_retriever_chain(llm, retriever)
            
            # Retrieve documents
            docs = self.retrieve_documents(doc_retriever, messages)
            
            if docs:
                # Format documents and get RAG response
                formatted_docs, sources = self.format_documents(docs, model, chat_mode_settings)
                rag_chain = self.get_rag_chain(llm)
                
                ai_response = rag_chain.invoke({
                    "messages": messages[:-1],
                    "context": formatted_docs,
                    "input": question
                })
                
                content = ai_response.content
            else:
                content = "I couldn't find any relevant documents to answer your question."
                sources = []
            
            response_time = time.time() - start_time
            
            return {
                "message": content,
                "model": model_name,
                "sources": sources,
                "response_time": response_time,
                "mode": chat_mode_settings["mode"],
                "nodedetails": {"chunkdetails": []},
                "entities": {},
                "total_tokens": 0  # Could implement token counting
            }
            
        except Exception as e:
            logger.error(f"Error processing vector chat: {e}")
            return {
                "message": "Something went wrong with the search",
                "model": model,
                "sources": [],
                "response_time": 0,
                "mode": chat_mode_settings["mode"],
                "error": str(e)
            }
    
    def clear_chat_history(self, session_id: str) -> Dict[str, Any]:
        """Clear chat history for a session"""
        try:
            history = SessionChatHistory.get_chat_history(session_id)
            history.clear()
            
            return {
                "session_id": session_id,
                "message": "The chat history has been cleared.",
                "user": "chatbot"
            }
            
        except Exception as e:
            logger.error(f"Error clearing chat history for session {session_id}: {e}")
            return {
                "session_id": session_id,
                "message": "Failed to clear chat history.",
                "user": "chatbot"
            }
    
    def process_chat(self, question: str, model: str, mode: str, 
                    document_names: Optional[List[str]], session_id: str) -> Dict[str, Any]:
        """Main chat processing method"""
        try:
            logger.info(f"Processing chat - Mode: {mode}, Model: {model}, Session: {session_id}")
            
            # Get chat history
            history = SessionChatHistory.get_chat_history(session_id)
            messages = list(history.messages)
            
            # Add user question
            user_question = HumanMessage(content=question)
            messages.append(user_question)
            
            if mode == "graph":
                # Graph mode
                result = self.graph_service.query_graph(question, model)
            else:
                # Vector modes
                chat_mode_settings = self.get_chat_mode_settings(mode)
                
                # Check document filter compatibility
                if document_names and not chat_mode_settings.get("document_filter", True):
                    result = {
                        "message": "Please deselect all documents in the table before using this chat mode",
                        "model": model,
                        "sources": [],
                        "response_time": 0,
                        "mode": mode,
                        "entities": {},
                        "nodedetails": {}
                    }
                else:
                    result = self.process_vector_chat(question, model, document_names, chat_mode_settings, messages)
            
            # Add AI response to history
            ai_response = AIMessage(content=result["message"])
            messages.append(ai_response)
            history.add_message(ai_response)
            
            # Add session ID to result
            result["session_id"] = session_id
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing chat: {e}")
            return {
                "session_id": session_id,
                "message": "Something went wrong",
                "model": model,
                "sources": [],
                "response_time": 0,
                "mode": mode,
                "error": str(e)
            }
