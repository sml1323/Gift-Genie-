# Gift Genie Backend

FastAPI backend implementation for the Gift Genie AI recommendation service.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```bash
# Required for AI recommendations
OPENAI_API_KEY=your-openai-api-key-here

# Optional for enhanced MCP pipeline
BRAVE_SEARCH_API_KEY=your-brave-search-api-key-here
APIFY_API_KEY=your-apify-api-key-here
```

### 3. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 📡 API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with service info
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed service status

### Recommendation Endpoints

- `POST /api/v1/recommendations` - Default recommendations (enhanced mode)
- `POST /api/v1/recommendations/basic` - AI-only recommendations (fast)
- `POST /api/v1/recommendations/enhanced` - Full MCP pipeline (comprehensive)

### Example Request

```json
{
  "recipient_age": 28,
  "recipient_gender": "여성",
  "relationship": "친구",
  "budget_min": 50,
  "budget_max": 150,
  "interests": ["독서", "커피", "여행"],
  "occasion": "생일",
  "personal_style": "미니멀리스트",
  "restrictions": ["쥬얼리 제외"]
}
```

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
# Start the server in one terminal
python main.py

# Run tests in another terminal
python test_api.py
```

## 🏗️ Architecture

### Core Components

- **AI Engine**: GPT-4o-mini powered recommendation generation
- **MCP Pipeline**: Brave Search + Apify for real product data
- **FastAPI**: Modern async web framework
- **Pydantic**: Data validation and serialization

### Service Layers

```
┌─────────────────┐
│   FastAPI API   │  ← HTTP endpoints
├─────────────────┤
│ Recommendation  │  ← Business logic
│    Services     │
├─────────────────┤
│ MCP Integration │  ← External APIs
│   (Brave/Apify) │
├─────────────────┤
│   OpenAI API    │  ← AI recommendations
└─────────────────┘
```

### Response Modes

1. **Basic Mode** (`/basic`): AI-only, fast response (~2-3s)
2. **Enhanced Mode** (`/enhanced`): Full MCP pipeline (~5-10s)
3. **Default Mode** (`/recommendations`): Enhanced by default

## 🔧 Configuration

All configuration is handled through environment variables. See `.env.example` for all available options.

### Simulation Mode

If API keys are not configured, the service runs in simulation mode:
- ✅ AI recommendations work with mock data
- ✅ MCP pipeline simulates search and scraping
- ✅ Full API compatibility maintained

### Production Settings

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

## 🚨 Error Handling

The API includes comprehensive error handling:

- **Validation Errors**: 422 with detailed field information
- **API Failures**: Graceful fallback to simulation mode
- **Rate Limiting**: Configurable per-minute limits
- **Timeouts**: 30-second API timeout with async processing

## 📊 Performance

### Expected Response Times

- Basic recommendations: 1-3 seconds
- Enhanced recommendations: 5-10 seconds
- Health checks: <100ms

### Scaling Considerations

- Stateless design for horizontal scaling
- Async processing for concurrent requests
- Built-in caching capabilities (future)
- Database integration ready (future)

## 🔍 Monitoring

### Health Endpoints

- `/api/v1/health` - Quick status check
- `/api/v1/health/detailed` - Full service status including:
  - API key configuration status
  - Service availability
  - Feature flags

### Logging

Structured logging with different levels:
- `INFO`: Request/response logging
- `WARNING`: API fallbacks and retries
- `ERROR`: Failed requests and exceptions

## 🛠️ Development

### Project Structure

```
backend/
├── app/
│   ├── core/              # Configuration
│   └── routers/           # API endpoints
├── models/
│   ├── request/           # Request schemas
│   └── response/          # Response schemas
├── services/
│   ├── ai/                # AI recommendation engine
│   ├── search/            # Brave Search integration
│   └── scraping/          # Apify scraping service
├── main.py                # FastAPI application
├── requirements.txt       # Dependencies
└── test_api.py           # Test suite
```

### Adding New Features

1. Add Pydantic models in `models/`
2. Implement business logic in `services/`
3. Create API endpoints in `app/routers/`
4. Update tests in `test_api.py`

---

**Built with FastAPI** ⚡ **Powered by OpenAI GPT-4o-mini** 🤖 **Enhanced by MCP** 🔍