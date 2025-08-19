# AI Assistant with Web Search

An intelligent AI Assistant that can answer questions using web search and local or cloud-based LLMs.

## 🌟 Features

- **Web Search Integration**: Performs web searches using Brave Search API or SearXNG
- **Multi-LLM Support**: Switch between local (Ollama) and cloud (OpenAI) LLMs
- **Interactive Chat Interface**: Clean, modern UI with conversation history
- **Smart Web Search**: Automatically detects when to perform web searches
- **Source Citation**: Includes sources from web search results
- **Streaming Responses**: Real-time response generation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed (for local LLMs)
- Brave API key (for web search)
- OpenAI API key (if using OpenAI models)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Copy the example environment file:
```bash
cp .env.example .env
```
4. Edit `.env` with your configuration (see below)

## ⚙️ Configuration

Edit the `.env` file with your preferred settings:

```env
# LLM Provider Configuration
LLM_PROVIDER=ollama  # 'openai' or 'ollama'

# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# For Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:7b

# Web Search Configuration
BRAVE_API_KEY=your_brave_api_key_here
SEARXNG_BASE_URL=http://localhost:8081

# Server Configuration
HOST=0.0.0.0
PORT=8135
```

## 🏃‍♀️ Running the Application

### 1. Start the FastAPI Server

In one terminal, start the FastAPI server:

```bash
python server.py
```

### 2. Start the Streamlit UI

In another terminal, start the Streamlit interface:

```bash
streamlit run app.py
```

The web interface will open automatically in your default browser at `http://localhost:8501`.

## 🎯 Usage

1. Type your question in the chat input
2. Toggle "Enable Web Search" in the sidebar to allow the AI to search the web
3. The AI will generate a response, optionally using web search results
4. Click on "View search results" to see the sources used
5. Use the sidebar to switch between different LLM providers and models

## 🤖 Available Models

### Local Models (via Ollama)
- qwen2:7b
- llama2
- mistral
- gemma
- or any other model supported by Ollama

### Cloud Models (via OpenAI)
- gpt-3.5-turbo
- gpt-4
- gpt-4-turbo

## Usage

The agent can be used through the MCP server interface. It provides a `web_search` tool that can be called with a search query.

Example usage:
```python
# Using the MCP client
client = MCPClient("http://localhost:8000")
results = client.call("web_search", "What is the capital of France?")
```

## Development

The project follows these conventions:
- Python files should not exceed 500 lines
- Code is organized into modules by feature
- Unit tests are required for new features
- Code follows PEP8 style guidelines
- Docstrings use Google style format

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
