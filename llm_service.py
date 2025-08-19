import os
from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
from openai import AsyncOpenAI
import ollama
import asyncio

class LLMProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"

class LLMService:
    def __init__(self):
        self.provider = os.getenv('LLM_PROVIDER', 'ollama').lower()
        self.model = os.getenv('LLM_MODEL', 'qwen2.5:7b')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        if self.provider == LLMProvider.OPENAI and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        if self.provider == LLMProvider.OPENAI:
            return AsyncOpenAI(
                api_key=self.openai_api_key,
                base_url=self.openai_base_url
            )
        return None  # For Ollama, we'll use the ollama package directly
    
    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text using the configured LLM provider."""
        if self.provider == LLMProvider.OPENAI:
            return await self._generate_openai(prompt, max_tokens)
        else:
            return await self._generate_ollama(prompt, max_tokens)
    
    async def _generate_openai(self, prompt: str, max_tokens: int) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _generate_ollama(self, prompt: str, max_tokens: int) -> str:
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"num_predict": max_tokens, "temperature": 0.7}
                )
            )
            return response['message']['content']
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")

# Initialize a global LLM service instance
llm_service = LLMService()

# Utility function for summarization
async def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Generate a summary of the given text."""
    prompt = f"""
    Please provide a concise summary of the following text in {max_sentences} sentences or less.
    Focus on the key points and main ideas.
    
    Text to summarize:
    {text}
    
    Summary:
    """
    return await llm_service.generate(prompt)

# Web search agent integration
async def generate_web_aware_response(query: str, search_results: List[Dict[str, str]]) -> str:
    """Generate a response that incorporates web search results."""
    context = "\n\n".join(
        f"Source {i+1}: {res['title']}\nURL: {res['url']}\nContent: {res['snippet']}"
        for i, res in enumerate(search_results)
    )
    
    prompt = f"""
    You are a helpful AI assistant that can answer questions using web search results.
    
    User's question: {query}
    
    Here are some relevant search results:
    {context}
    
    Based on the above information, please provide a clear and concise answer to the user's question.
    If the search results don't contain enough information to answer the question, please say so.
    Include relevant source numbers (e.g., [1], [2]) to cite your information.
    
    Answer:
    """
    
    return await llm_service.generate(prompt)
