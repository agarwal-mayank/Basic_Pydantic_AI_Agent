from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
import httpx
from httpx import HTTPStatusError, TimeoutException
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()


class SearchResults(BaseModel):
    """Represents a single search result with title, URL, snippet, and optional score."""

    title: str = Field(description="Title of the search result")
    url: str = Field(description="URL of the search result")
    snippet: str = Field(description="Snippet of the search result content")
    score: Optional[float] = Field(
        default=None, description="Relevance score of the result"
    )


class SearchError(Exception):
    """Base exception for search-related errors."""

    pass


class WebSearchTool:
    """Tool for performing web searches using either Brave Search API or SearXNG."""

    def __init__(self):
        """Initialize search tool with configuration from environment variables."""
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        self.searxng_base_url = os.getenv("SEARXNG_BASE_URL")
        self.provider = "brave" if self.brave_api_key else "searxng"

        if not any([self.brave_api_key, self.searxng_base_url]):
            raise SearchError(
                "No search provider configured. Please set either BRAVE_API_KEY or SEARXNG_BASE_URL"
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def search_brave(self, query: str) -> List[SearchResults]:
        """
        Perform a web search using Brave Search API.

        Args:
            query (str): Search query to perform

        Returns:
            List[SearchResults]: List of search results

        Raises:
            SearchError: If API key is not configured or API request fails
        """
        if not self.brave_api_key:
            raise SearchError("BRAVE_API_KEY not set in environment variables")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": 5},
                    headers={"X-Subscription-Token": self.brave_api_key},
                    timeout=10.0,
                )

                response.raise_for_status()
                data = response.json()

                results = []
                # Handle the new response format
                if "web" in data and "results" in data["web"]:
                    for item in data["web"]["results"]:
                        try:
                            result = SearchResults(
                                title=item.get("title", ""),
                                url=item.get("url", ""),
                                snippet=item.get("description", ""),
                                score=item.get("score", 0.0),
                            )
                            results.append(result)
                        except Exception as e:
                            print(f"Warning: Failed to process Brave search result: {e}")
                else:
                    # Fallback to direct iteration if structure is different
                    for item in data.get("results", []):
                        try:
                            result = SearchResults(
                                title=item.get("title", ""),
                                url=item.get("url", ""),
                                snippet=item.get("description", ""),
                                score=item.get("score", 0.0),
                            )
                            results.append(result)
                        except Exception as e:
                            print(f"Warning: Failed to process Brave search result (fallback): {e}")

                return results

        except HTTPStatusError as e:
            raise SearchError(
                f"Brave API error: {e.response.status_code} - {e.response.text}"
            )
        except TimeoutException:
            raise SearchError("Brave API request timed out")
        except Exception as e:
            raise SearchError(f"Unexpected error in Brave search: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def search_searxng(self, query: str) -> List[SearchResults]:
        """
        Perform a web search using SearXNG.

        Args:
            query (str): Search query to perform

        Returns:
            List[SearchResults]: List of search results

        Raises:
            SearchError: If base URL is not configured or API request fails
        """
        if not self.searxng_base_url:
            raise SearchError("SEARXNG_BASE_URL not set in environment variables")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.searxng_base_url}/search",
                    params={
                        "q": query,
                        "format": "json",
                        "language": "en-US",
                        "num": 5,
                    },
                    timeout=10.0,
                )

                await response.raise_for_status()
                data = await response.json()

                results = []
                for item in data.get("results", []):
                    try:
                        result = SearchResults(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            snippet=item.get("content", ""),
                        )
                        results.append(result)
                    except Exception as e:
                        print(f"Warning: Failed to process SearXNG search result: {e}")

                return results

        except HTTPStatusError as e:
            raise SearchError(
                f"SearXNG API error: {e.response.status_code} - {e.response.text}"
            )
        except TimeoutException:
            raise SearchError("SearXNG API request timed out")
        except Exception as e:
            raise SearchError(f"Unexpected error in SearXNG search: {str(e)}")

    async def search(self, query: str) -> List[SearchResults]:
        """
        Perform a web search using the configured provider.

        Args:
            query (str): Search query to perform

        Returns:
            List[SearchResults]: List of search results

        Raises:
            SearchError: If no provider is configured or search fails
        """
        print(f"[DEBUG] Starting search with provider: {self.provider}")
        if not self.provider:
            error_msg = "No search provider configured"
            print(f"[ERROR] {error_msg}")
            raise SearchError(error_msg)

        try:
            if self.provider == "brave":
                print("[DEBUG] Using Brave search")
                results = await self.search_brave(query)
            else:
                print("[DEBUG] Using SearXNG search")
                results = await self.search_searxng(query)
            
            print(f"[DEBUG] Search returned {len(results) if results else 0} results")
            return results
            
        except SearchError as e:
            print(f"[ERROR] Search failed: {str(e)}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error in search: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise SearchError(error_msg) from e


class WebSearchAgent:
    """Agent that provides web search capabilities using either Brave or SearXNG."""

    def __init__(self):
        """Initialize the search agent with the configured search tool."""
        self.search_tool = WebSearchTool()

    async def search_web(self, query: str) -> List[Dict[str, Any]]:
        """
        Main search function that performs web search using the configured provider.

        Args:
            query (str): Search query to perform

        Returns:
            List[Dict[str, Any]]: List of search results as dictionaries
        """
        print(f"[DEBUG] Starting search for query: {query}")
        try:
            results = await self.search_tool.search(query)
            print(f"[DEBUG] Raw search results: {results}")
            
            # Convert results to dictionaries if they're Pydantic models
            if results and hasattr(results[0], 'model_dump'):
                results = [result.model_dump() for result in results]
            elif results and hasattr(results[0], 'dict'):  # For older Pydantic versions
                results = [result.dict() for result in results]
            
            print(f"[DEBUG] Processed {len(results)} results")
            return results
            
        except SearchError as e:
            error_msg = f"Search error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error in search_web: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise Exception(error_msg) from e
