# Voice Memo App

A voice memo application that uses AI to transcribe, summarize, and make voice memos searchable using semantic search.

## Features

- 🎙️ Voice memo transcription using OpenAI Whisper
- 🤖 Automatic title generation using Claude AI
- 🔍 Semantic search across your memos using vector embeddings
- 📱 Telegram bot interface
- 📊 Prometheus metrics integration
- 🔐 User-based access control

## Architecture

The application is built using a modern, microservices-based architecture:

- FastAPI backend service for core functionality
- Telegram bot service for user interaction
- Vector database (Pinecone) for semantic search
- Local JSON storage for memo data

## Tech Stack

- **Backend Framework**: FastAPI
- **AI Services**: 
  - OpenAI (Whisper, Ada)
  - Anthropic Claude
- **Vector Database**: Pinecone
- **Containerization**: Docker
- **Monitoring**: Prometheus
- **Testing**: pytest
- **Code Quality**: Black

## Installation

1. Create and configure environment files:

For the API service (`src/config/.env`):
```bash
openai_api_key=your_openai_key
pinecone_api_key=your_pinecone_key
pinecone_host=your_pinecone_host
claude_api_key=your_claude_key
```

For the Telegram bot (`src/clients/telegram_client/.env`):
```bash
telegram_api_token=your_telegram_token
api_base_url=http://memo_api:8000
```

2. Build and start the services:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

## Development Setup

1. Install UV if you haven't already:
```bash
pip install uv
```

2. Install dependencies:
```bash
uv sync
```

This will install all dependencies, including development dependencies, in a new virtual environment managed by UV.

3. Run tests:
```bash
uv run pytest
```

## API Documentation

The API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

- `POST /memos/`: Create a new voice memo
- `POST /search/`: Search through existing memos

## Telegram Bot Usage

1. Start a chat with your bot
2. Send voice messages to create memos
3. Send text messages to search through your memos

## Project Structure

```
.
├── src/
│   ├── api/             # FastAPI application
│   ├── clients/         # Client applications (Telegram)
│   ├── core/            # Core business logic
│   ├── infrastructure/  # External services integration
│   └── config/          # Configuration management
├── tests/               # Test suite
└── docker/              # Docker configuration
```


