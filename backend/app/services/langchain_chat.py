"""
LangChain-based conversational chat service with prompt chaining
"""
import os
import time
from typing import Generator, List, Dict, Any, Optional
try:
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.chains import ConversationChain
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema.output_parser import StrOutputParser
    from langchain.schema.runnable import RunnablePassthrough
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class ConversationalChatService:
    """LangChain-based conversational chat with memory"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain not installed. Please install with: pip install langchain langchain-google-genai")
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.7,
            max_output_tokens=2048
        )
        
        # Create conversation memory
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True,
            memory_key="chat_history"
        )
    
    def create_contextual_prompt(self, context: str, conversation_history: str = "") -> ChatPromptTemplate:
        """Create a contextual prompt template"""
        
        system_prompt = """You are a helpful AI assistant that answers questions based on provided documents and maintains conversation context.

IMPORTANT RULES:
1. Use ONLY the provided document context to answer questions
2. If the context doesn't contain enough information, say so clearly
3. Do NOT include citations or source references like [Source 1] in your response
4. Maintain conversation flow and reference previous questions when relevant
5. Be conversational and helpful
6. If asked about something not in the documents, politely explain you can only answer based on the provided content
7. Provide well-structured, clear responses similar to ChatGPT

DOCUMENT CONTEXT:
{context}

CONVERSATION HISTORY:
{conversation_history}

Current Question: {question}

Please provide a helpful response based on the documents and conversation context."""

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}")
        ])
    
    def chat_stream(self, question: str, context: str, conversation_history: str = "") -> Generator[str, None, None]:
        """Stream chat response with conversation context"""
        try:
            # Create prompt template
            prompt_template = self.create_contextual_prompt(context, conversation_history)
            
            # Create chain
            chain = prompt_template | self.llm | StrOutputParser()
            
            # Get response
            response = chain.invoke({
                "context": context,
                "conversation_history": conversation_history,
                "question": question
            })
            
            # Stream response word by word
            words = response.split()
            for word in words:
                yield word + " "
                time.sleep(0.03)  # Typing effect
                
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def chat_with_memory(self, question: str, context: str, session_id: str) -> Generator[str, None, None]:
        """Chat with persistent memory across sessions"""
        try:
            # Add current question to memory
            self.memory.chat_memory.add_user_message(question)
            
            # Create system message with context
            system_message = f"""You are a helpful AI assistant. Use ONLY the provided document context to answer questions.

DOCUMENT CONTEXT:
{context}

Be conversational and reference previous parts of our conversation when relevant. Do NOT include citations or source references in your response. Provide clear, well-structured answers similar to ChatGPT."""

            # Create messages for the LLM
            messages = [
                SystemMessage(content=system_message),
                *self.memory.chat_memory.messages,
                HumanMessage(content=question)
            ]
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            
            # Add response to memory
            self.memory.chat_memory.add_ai_message(response.content)
            
            # Stream response
            words = response.content.split()
            for word in words:
                yield word + " "
                time.sleep(0.03)
                
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()

class DocumentAwareChatService:
    """Enhanced chat service with document awareness and conversation flow"""
    
    def __init__(self):
        self.chat_service = ConversationalChatService()
    
    def create_conversation_chain(self, context: str) -> ConversationChain:
        """Create a conversation chain with document context"""
        
        # System prompt with document context
        system_prompt = f"""You are a helpful AI assistant that answers questions based on the provided documents.

DOCUMENT CONTEXT:
{context}

RULES:
1. Use ONLY the provided document context to answer questions
2. Do NOT include citations or source references like [Source 1] in your response
3. If context doesn't contain enough information, say so
4. Be conversational and reference previous questions when relevant
5. Maintain natural conversation flow
6. Provide clear, well-structured responses similar to ChatGPT"""

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # Create conversation chain
        chain = ConversationChain(
            llm=self.chat_service.llm,
            memory=self.chat_service.memory,
            prompt=prompt,
            verbose=False
        )
        
        return chain
    
    def chat_with_documents(self, question: str, context: str, session_id: str) -> Generator[str, None, None]:
        """Chat with document context and conversation memory"""
        try:
            # Create conversation chain
            chain = self.create_conversation_chain(context)
            
            # Get response
            response = chain.predict(input=question)
            
            # Stream response
            words = response.split()
            for word in words:
                yield word + " "
                time.sleep(0.03)
                
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            "total_exchanges": len(self.chat_service.memory.chat_memory.messages) // 2,
            "memory_type": "ConversationBufferWindowMemory",
            "window_size": self.chat_service.memory.k
        }