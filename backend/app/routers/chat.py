from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..schemas.chat import ChatIn
from ..memory import SESSIONS
from ..services.retrieve import top_k
from ..services.pack import pack_context
from ..services.llm import answer_stream
from ..services.conversation import conversation_manager
from ..services.simple_chat import SimpleConversationalChat

router = APIRouter()

# Initialize chat service with fallback
try:
    from ..services.langchain_chat import DocumentAwareChatService
    chat_service = DocumentAwareChatService()
    print("✓ Using LangChain-based chat service")
except (ImportError, ValueError) as e:
    # Fallback to simple chat service if LangChain not available or API key missing
    print(f"⚠ Falling back to SimpleConversationalChat: {e}")
    chat_service = SimpleConversationalChat()

@router.post("/stream")
def chat_stream(payload: ChatIn):
    s = SESSIONS.get(payload.session_id)
    if not s.ready or not s.chunks:
        raise HTTPException(400, "no indexed content; upload first")

    hits = top_k(payload.message, s, k=payload.k or 8)
    if not hits:
        def gen_insufficient():
            yield "data: insufficient evidence in sources\n\n"
            yield "event:done\ndata:ok\n\n"
        return StreamingResponse(gen_insufficient(), media_type="text/event-stream")

    ctx = pack_context(hits, budget_chars=payload.max_ctx or 6000)
    sys = "You are a helpful assistant. Use ONLY the provided context to answer questions. Provide clear, well-structured responses without citations. If the context doesn't contain enough information to answer, say so clearly."
    prompt = f"{sys}\n\nCONTEXT:\n{ctx}\n\nUSER QUESTION: {payload.message}\n\nASSISTANT RESPONSE:"

    def gen():
        # Cleaner metadata format
        sources = [{"source_id": h["source_id"], "chunk": h["span"]["chunk"]} for h in hits]
        yield f"event:meta\ndata:{sources}\n\n"
        
        # Stream response in readable chunks
        for token in answer_stream(prompt):
            yield f"data:{token}\n\n"
        yield "event:done\ndata:ok\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")

@router.post("/conversational")
def chat_conversational(payload: ChatIn):
    """
    Conversational chat endpoint with memory and prompt chaining
    Like NotebookLM/ChatGPT experience
    """
    s = SESSIONS.get(payload.session_id)
    if not s.ready or not s.chunks:
        raise HTTPException(400, "no indexed content; upload first")

    # Get relevant chunks
    hits = top_k(payload.message, s, k=payload.k or 8)
    if not hits:
        def gen_insufficient():
            yield "data: I don't have enough information in the documents to answer that question.\n\n"
            yield "event:done\ndata:ok\n\n"
        return StreamingResponse(gen_insufficient(), media_type="text/event-stream")

    # Pack context
    ctx = pack_context(hits, budget_chars=payload.max_ctx or 6000)
    
    # Get conversation history
    conversation = conversation_manager.get_conversation(payload.session_id)
    conversation_history = conversation.get_recent_context(last_n=5)
    
    def gen():
        # Send metadata
        sources = [{"source_id": h["source_id"], "chunk": h["span"]["chunk"]} for h in hits]
        yield f"event:meta\ndata:{sources}\n\n"
        
        # Stream conversational response and track full response
        assistant_response = ""
        try:
            # Check if we have LangChain service or simple service
            if hasattr(chat_service, 'chat_with_documents'):
                # LangChain service
                for token in chat_service.chat_with_documents(payload.message, ctx, payload.session_id):
                    assistant_response += token
                    yield f"data:{token}\n\n"
            else:
                # Simple service
                for token in chat_service.chat_with_documents(payload.message, ctx, conversation_history):
                    assistant_response += token
                    yield f"data:{token}\n\n"
            
            # Save both user and assistant messages to conversation memory
            conversation.add_message("user", payload.message, sources)
            conversation.add_message("assistant", assistant_response.strip())
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data:{error_msg}\n\n"
            # Still save the conversation even if there's an error
            conversation.add_message("user", payload.message, sources)
            conversation.add_message("assistant", error_msg)
        
        yield "event:done\ndata:ok\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")

@router.post("/conversation/clear")
def clear_conversation(payload: ChatIn):
    """Clear conversation history for a session"""
    conversation = conversation_manager.get_conversation(payload.session_id)
    conversation.clear()
    
    # Clear memory if LangChain service is available
    if hasattr(chat_service, 'chat_service'):
        chat_service.chat_service.clear_memory()
    
    return {"message": "Conversation cleared successfully"}

@router.get("/conversation/{session_id}/summary")
def get_conversation_summary(session_id: str):
    """Get conversation summary for a session"""
    conversation = conversation_manager.get_conversation(session_id)
    summary = conversation.get_summary()
    return summary