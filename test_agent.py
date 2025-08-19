import pytest
import os
from agent import WebSearchTool
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_env():
    os.environ["BRAVE_API_KEY"] = "test-brave-key"
    os.environ["SEARXNG_BASE_URL"] = "http://test-searxng-instance"
    yield
    del os.environ["BRAVE_API_KEY"]
    del os.environ["SEARXNG_BASE_URL"]

@pytest.mark.asyncio
async def test_search_brave(mock_env):
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "web": {
                "results": [
                    {
                        "title": "Test Page",
                        "url": "https://test.com",
                        "snippet": "Test snippet",
                        "score": 0.9
                    }
                ]
            }
        })
        mock_client.return_value.get.return_value = mock_response

        tool = WebSearchTool()
        results = await tool.search_brave("test query")
        
        assert len(results) == 1
        assert results[0].title == "Test Page"
        assert results[0].url == "https://test.com"
        assert results[0].snippet == "Test snippet"
        assert results[0].score == 0.9

@pytest.mark.asyncio
async def test_search_searxng(mock_env):
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "results": [
                {
                    "title": "Test Page",
                    "url": "https://test.com",
                    "content": "Test content"
                }
            ]
        })
        mock_client.return_value.get.return_value = mock_response

        tool = WebSearchTool()
        results = await tool.search_searxng("test query")
        
        assert len(results) == 1
        assert results[0].title == "Test Page"
        assert results[0].url == "https://test.com"
        assert results[0].snippet == "Test content"

@pytest.mark.asyncio
async def test_search_provider_selection(mock_env):
    # Test Brave selection
    tool = WebSearchTool()
    assert tool.provider == "brave"

    # Test SearXNG selection
    del os.environ["BRAVE_API_KEY"]
    tool = WebSearchTool()
    assert tool.provider == "searxng"
