"""
Simple conversational chat service without LangChain dependency
"""
import os
import time
from typing import Generator
from ..services.llm import answer_stream

class SimpleConversationalChat:
    """Simple conversational chat with basic memory"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
    
    def chat_with_documents(self, question: str, context: str, conversation_history: str = "") -> Generator[str, None, None]:
        """Simple chat with document context and conversation history"""
        
        # Create a conversational prompt
        if conversation_history:
            prompt = f"""You are a helpful AI assistant. Use ONLY the provided document context to answer questions.

DOCUMENT CONTEXT:
{context}

CONVERSATION HISTORY:
{conversation_history}

Current Question: {question}

Please provide a helpful, well-structured response based on the documents and conversation context. Be conversational and reference previous parts of our conversation when relevant. Do not include citations or source references in your response."""
        else:
            prompt = f"""You are a helpful AI assistant. Use ONLY the provided document context to answer questions.

DOCUMENT CONTEXT:
{context}

Current Question: {question}

Please provide a helpful, well-structured response based on the documents. Do not include citations or source references in your response."""
        
        # Stream response using the existing LLM service
        for token in answer_stream(prompt):
            yield token