import os
import streamlit as st
import httpx
import asyncio
import json
from typing import List, Dict, Optional, Tuple
from enum import Enum
import uuid
from datetime import datetime
from llm_service import llm_service, summarize_text, generate_web_aware_response

# Configure the page
st.set_page_config(
    page_title="AI Assistant with Web Search", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #f0f2f6;
        margin-left: 20%;
        border-bottom-right-radius: 0;
    }
    .chat-message.assistant {
        background-color: #e3f2fd;
        margin-right: 20%;
        border-bottom-left-radius: 0;
    }
    .chat-message .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        margin-right: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
    .user .avatar {
        background-color: #4a90e2;
        color: white;
    }
    .assistant .avatar {
        background-color: #34a853;
        color: white;
    }
    .chat-message .content {
        flex: 1;
    }
    .chat-message .timestamp {
        font-size: 0.75rem;
        color: #666;
        margin-top: 0.25rem;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
    }
    .stTextInput>div>div>input {
        padding: 0.75rem;
    }
    .search-results {
        margin-top: 1rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
    }
    .result-card {
        padding: 0.75rem;
        margin-bottom: 0.75rem;
        border-radius: 0.5rem;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .result-title {
        color: #1a73e8;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .result-url {
        color: #5f6368;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
        word-break: break-all;
    }
    .result-snippet {
        color: #3c4043;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .stSpinner > div {
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize web search toggle
if "use_web_search" not in st.session_state:
    st.session_state.use_web_search = True

# Initialize LLM provider
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "ollama"  # Default to Ollama

# Initialize asyncio event loop
if not hasattr(st.session_state, 'loop'):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    st.session_state.loop = loop

# Sidebar configuration
st.sidebar.title("⚙️ Settings")

# Server configuration
st.sidebar.subheader("API Configuration")
SERVER_URL = st.sidebar.text_input(
    "Server URL",
    value="http://localhost:8135",
    help="URL where your FastAPI server is running"
)

# LLM configuration
st.sidebar.subheader("LLM Configuration")
llm_provider = st.sidebar.selectbox(
    "LLM Provider",
    ["Ollama (Local)", "OpenAI"],
    index=0 if os.getenv("LLM_PROVIDER", "ollama").lower() == "ollama" else 1
)

if llm_provider == "OpenAI":
    os.environ["LLM_PROVIDER"] = "openai"
    model_name = st.sidebar.text_input(
        "OpenAI Model",
        value=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        help="The OpenAI model to use (e.g., gpt-3.5-turbo, gpt-4)"
    )
    os.environ["OPENAI_MODEL"] = model_name
else:
    os.environ["LLM_PROVIDER"] = "ollama"
    model_name = st.sidebar.text_input(
        "Ollama Model",
        value=os.getenv("OLLAMA_MODEL", "qwen2:7b"),
        help="The Ollama model to use (e.g., llama2, mistral, qwen2:7b)"
    )
    os.environ["OLLAMA_MODEL"] = model_name

# Web search toggle
st.session_state.use_web_search = st.sidebar.toggle(
    "Enable Web Search",
    value=st.session_state.get("use_web_search", False),
    help="Enable to perform web searches for factual information"
)

# Clear chat button
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.session_state.search_results = {}
    st.rerun()

# Add some instructions in the sidebar
st.sidebar.markdown("## How to use")
st.sidebar.markdown("""
1. Type your message in the chat input below
2. Toggle "Enable Web Search" to let the AI search the web for information
3. The AI will respond using the selected LLM
4. Click "Clear Chat" to start a new conversation
""")

# Chat interface
st.title("🤖 AI Assistant")
st.caption(f"Using {llm_provider} with {model_name}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "search_results" in message and message["search_results"]:
            with st.expander("View search results"):
                for i, result in enumerate(message["search_results"], 1):
                    with st.container():
                        st.markdown(
                            f"""
                            <div class="result-card">
                                <div class="result-title">{i}. {result.get('title', 'No title')}</div>
                                <div class="result-url">{result.get('url', '')}</div>
                                <div class="result-snippet">{result.get('snippet', 'No description available.')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

# Function to perform search
async def perform_search(query: str) -> List[Dict]:
    """Send search request to the FastAPI server"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVER_URL}/search",
                json={"query": query},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Error performing search: {str(e)}")
        return []

# Function to get AI response
async def get_ai_response(query: str, search_results: List[Dict] = None) -> str:
    """Get response from the LLM, optionally using web search results."""
    if search_results and len(search_results) > 0:
        return await generate_web_aware_response(query, search_results)
    else:
        return await llm_service.generate(f"User: {query}\n\nAssistant:")

async def process_chat(prompt):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        search_results = []
        
        # Check if web search is enabled and the query seems to require factual information
        perform_web_search = st.session_state.use_web_search and any(
            keyword in prompt.lower() 
            for keyword in ["what", "when", "where", "who", "how", "why", "current", "latest", "recent", "update"]
        )
        
        try:
            if perform_web_search:
                with st.spinner("🔍 Searching the web..."):
                    search_results = await perform_search(prompt)
                    
                    if search_results:
                        with st.expander("View search results", expanded=False):
                            for i, result in enumerate(search_results, 1):
                                with st.container():
                                    st.markdown(
                                        f"""
                                        <div class="result-card">
                                            <div class="result-title">{i}. {result.get('title', 'No title')}</div>
                                            <div class="result-url">{result.get('url', '')}</div>
                                            <div class="result-snippet">{result.get('snippet', 'No description available.')}</div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
            
            # Get AI response
            with st.spinner("🧠 Thinking..."):
                response = await get_ai_response(prompt, search_results if perform_web_search else None)
                
                # Stream the response
                for chunk in response.split():
                    full_response += chunk + " "
                    message_placeholder.markdown(full_response + "▌")
                    await asyncio.sleep(0.02)  # Small delay for streaming effect
                
                message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "search_results": search_results if perform_web_search else None
                })
                
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "search_results": None
            })

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Create a new event loop for each interaction
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(process_chat(prompt))
    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
    finally:
        loop.close()
