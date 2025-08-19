# Web Search AI Agent - Project Planning

## Project Overview

This project aims to create a Pydantic AI Agent capable of performing web searches using either Brave Search API or SearXNG. The agent will be flexible, allowing users to choose between the two search providers based on their preferences and available resources.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Pydantic AI    │───▶│   Web Search    │
│                 │    │     Agent       │    │   (Brave/SearX) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │   LLM Provider  │
                       │ (OpenAI/Ollama) │
                       └─────────────────┘
```

## Core Components

### 1. Environment Configuration
- **LLM Provider Selection**: Support for OpenAI, OpenRouter, and Ollama
- **Search Provider Selection**: Brave API or SearXNG endpoint
- **Flexible Configuration**: Environment variables to control all aspects

### 2. Search Functions
- **Brave Search Integration**: REST API calls to Brave Search
- **SearXNG Integration**: HTTP requests to SearXNG instance
- **Dynamic Selection**: Runtime choice based on environment configuration

### 3. Pydantic AI Agent
- **Tool Integration**: Web search as agent tool
- **Response Processing**: Parse and format search results
- **Context Awareness**: Maintain conversation context while searching

### 4. MCP Server (FastMCP)
- **Server Framework**: Use FastMCP for MCP server implementation
- **Agent Exposure**: Expose the AI agent through MCP protocol
- **Tool Registration**: Register web search capabilities

## Technical Stack

### Primary Dependencies
- **Pydantic AI**: Core agent framework
- **FastMCP**: MCP server implementation
- **httpx**: HTTP client for API calls
- **python-dotenv**: Environment variable management

### Optional Dependencies (based on LLM provider)
- **openai**: For OpenAI API integration
- **ollama**: For local Ollama integration

## Development Phases

### Phase 1: Foundation Setup
1. **Environment Structure**
   - Create `.env.example` file with all required variables
   - Set up project structure and dependencies
   - Initialize configuration management

2. **API Integration Research**
   - Study Brave Search API documentation
   - Research SearXNG API endpoints and formats
   - Define common interface for both search providers

### Phase 2: Core Implementation
1. **Search Functions**
   - Implement `search_brave()` function
   - Implement `search_searxng()` function
   - Create search provider factory/selector

2. **Pydantic AI Agent**
   - Define agent with web search tool
   - Implement result processing and formatting
   - Add error handling and fallback mechanisms

### Phase 3: MCP Server Integration
1. **FastMCP Setup**
   - Create MCP server with FastMCP
   - Register agent and tools
   - Implement proper request/response handling

2. **Testing and Validation**
   - Unit tests for search functions
   - Integration tests with different LLM providers
   - End-to-end testing through MCP interface

### Phase 4: Documentation and Deployment
1. **Documentation**
   - Update README.md with setup instructions
   - Document API usage and configuration
   - Create troubleshooting guide

2. **Deployment Preparation**
   - Docker containerization (optional)
   - Performance optimization
   - Security considerations

## Configuration Strategy

### Environment Variables
```bash
# LLM Configuration
LLM_PROVIDER=openai          # openai, openrouter, ollama
LLM_BASE_URL=                # Custom base URL if needed
LLM_API_KEY=                 # API key for provider
LLM_CHOICE=gpt-4             # Specific model selection

# Search Configuration
BRAVE_API_KEY=               # Brave Search API key (if using Brave)
SEARXNG_BASE_URL=            # SearXNG instance URL (if using SearXNG)
```

### Provider Selection Logic
- If `BRAVE_API_KEY` is set and valid → use Brave Search
- If `SEARXNG_BASE_URL` is set and accessible → use SearXNG
- If both are available → prefer Brave (or make configurable)
- If neither available → graceful degradation

## Key Design Decisions

### 1. Search Provider Abstraction
- Create common interface for both search providers
- Allow runtime switching based on configuration
- Maintain consistent result format regardless of provider

### 2. Error Handling Strategy
- Graceful degradation when search providers are unavailable
- Comprehensive logging for debugging
- User-friendly error messages

### 3. Result Processing
- Standardize search result format
- Extract key information (title, snippet, URL)
- Limit result count for optimal LLM processing

### 4. Security Considerations
- Secure API key management
- Input sanitization for search queries
- Rate limiting awareness for API calls

## Success Metrics

### Functional Requirements
- ✅ Agent can search using Brave API
- ✅ Agent can search using SearXNG
- ✅ Dynamic provider selection works
- ✅ MCP server exposes agent functionality
- ✅ Multiple LLM providers supported

### Quality Requirements
- ✅ Comprehensive error handling
- ✅ Clear documentation and setup guide
- ✅ Modular and maintainable code structure
- ✅ Proper logging and debugging capabilities

## Potential Challenges and Mitigations

### Challenge 1: API Rate Limits
- **Mitigation**: Implement request queuing and rate limiting
- **Monitoring**: Track API usage and implement alerts

### Challenge 2: Search Result Quality
- **Mitigation**: Result filtering and relevance scoring
- **Fallback**: Multiple search attempts with different queries

### Challenge 3: Provider Availability
- **Mitigation**: Health checks and automatic failover
- **Monitoring**: Provider status monitoring

### Challenge 4: LLM Context Limits
- **Mitigation**: Intelligent result truncation
- **Optimization**: Summarize results before LLM processing

## Future Enhancements

### Near-term Improvements
- Search result caching for repeated queries
- Advanced query preprocessing and optimization
- Multi-provider result aggregation

### Long-term Vision
- Support for additional search providers (Google, Bing, etc.)
- Semantic search capabilities
- Integration with vector databases for enhanced context