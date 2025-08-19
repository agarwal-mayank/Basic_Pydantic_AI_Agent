from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from agent import WebSearchAgent, SearchResults
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Web Search API", description="API for performing web searches")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = WebSearchAgent()

class SearchQuery(BaseModel):
    query: str

import traceback

@app.post("/search", response_model=List[Dict[str, str]])
async def search_web(search_query: SearchQuery):
    """
    Perform a web search
    
    Args:
        query: The search query string
        
    Returns:
        List of search results with title, url, and snippet
    """
    try:
        print(f"Received search query: {search_query.query}")
        results = await agent.search_web(search_query.query)
        print(f"Search completed with {len(results)} results")
        return [{"title": r['title'], "url": r['url'], "snippet": r['snippet']} for r in results]
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in search_web: {str(e)}\n{error_trace}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "traceback": error_trace
            }
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8135, reload=True)
