# EmberLearn Backend

AI-powered Python tutoring platform backend with FastAPI and multiple AI agents.

## Quick Start

### 1. Setup Environment

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Copy environment file
cp .env.example .env

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure OpenAI API

```bash
# Edit .env and add your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"
```

### 3. Run the Server

```bash
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Chat & Agents
- `POST /api/chat` - Chat (auto-routes to appropriate agent)
- `POST /api/triage` - Route query to specialist
- `POST /api/concepts` - Explain Python concepts
- `POST /api/code_review` - Review Python code
- `POST /api/debug` - Debug Python errors
- `POST /api/exercise` - Generate coding exercises
- `POST /api/progress` - Get learning progress

### Health
- `GET /health` - Health check
- `GET /api/status` - API status

## Project Structure

```
backend/
├── main.py              # Main FastAPI application
├── app/
│   ├── __init__.py
│   ├── config.py        # Configuration settings
│   ├── schemas.py       # Pydantic schemas
│   ├── auth.py          # Authentication service
│   ├── models.py        # SQLAlchemy models
│   ├── database.py      # Database connection
│   ├── agents.py        # AI agents
│   ├── triage_agent/    # Triage agent service
│   ├── concepts_agent/  # Concepts agent service
│   ├── code_review_agent/
│   ├── debug_agent/
│   ├── exercise_agent/
│   └── progress_agent/
├── tests/               # Test suite
├── pyproject.toml       # Project dependencies
├── .env.example         # Example environment variables
└── README.md           # This file
```

## Agents

### 1. Triage Agent
Routes student queries to the most appropriate specialist agent.

### 2. Concepts Agent
Explains Python concepts with clear analogies and code examples.

### 3. Code Review Agent
Analyzes code for correctness, style (PEP 8), and efficiency.

### 4. Debug Agent
Helps identify and fix Python errors, providing hints before solutions.

### 5. Exercise Agent
Generates coding challenges and practice problems at appropriate difficulty levels.

### 6. Progress Agent
Tracks and reports student learning progress, mastery scores, and streaks.

## Authentication

Uses JWT tokens with HS256 signing.

```bash
# Get token from login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Use token in subsequent requests
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/auth/me
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_auth.py -v
```

## Development

```bash
# Format code
black app/ main.py

# Lint
ruff check app/ main.py

# Type check
mypy app/ main.py
```

## Production Deployment

### Environment Variables
```bash
# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql+asyncpg://user:password@hostname:5432/emberlearn

# Strong JWT secret
JWT_SECRET_KEY=generate-with-openssl-rand-hex-32

# Production mode
DEBUG=false
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Run with Docker

```bash
docker build -t emberlearn-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY="sk-..." emberlearn-backend
```

## Troubleshooting

### OpenAI API Key Error
- Make sure `OPENAI_API_KEY` is set in `.env`
- Check that your API key is valid on OpenAI dashboard
- Verify you have API credits available

### Database Error
- Delete `emberlearn.db` to reset local database
- Run `python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"`

### CORS Error from Frontend
- Check that frontend URL is in `CORS_ORIGINS` in `.env`
- Default allows `localhost:3000` and `127.0.0.1:3000`

### Port Already in Use
- Change `PORT` in `.env`
- Or kill process: `lsof -ti:8000 | xargs kill -9`

## Next Steps

- [ ] Implement Kafka integration for event streaming
- [ ] Add Dapr sidecar for distributed state management
- [ ] Deploy to Kubernetes with Kong API Gateway
- [ ] Add database migrations with Alembic
- [ ] Setup CI/CD with GitHub Actions
- [ ] Add monitoring and logging with Datadog/ELK

## Contributing

1. Create a feature branch
2. Make changes and add tests
3. Run `pytest` and `ruff check`
4. Submit pull request

## License

MIT
