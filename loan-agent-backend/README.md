# Loan Agent Backend

FastAPI-based backend for the Loan Collection System with GenAI Integration.

## Features

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Async ORM with PostgreSQL
- **JWT Authentication** - Secure user authentication
- **GenAI Integration** - AI-powered case summarization, script generation, and intent analysis
- **Drools Integration** - Rules engine for compliance and case assignment
- **RabbitMQ** - Message queue for async tasks
- **Alembic** - Database migrations

## Setup

### Prerequisites

- Python 3.11+
- uv (package manager)
- Docker & Docker Compose

### Installation

1. Install dependencies:
```bash
uv pip install -e .
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Edit `.env` with your configuration

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Running Locally

```bash
# Start dependencies (PostgreSQL, Redis, RabbitMQ)
docker-compose up -d postgres redis rabbitmq

# Run the application
uvicorn app.main:app --reload --port 8000
```

### Running with Docker

```bash
# Build and run all services
docker-compose up --build
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── api/
│   └── v1/           # API endpoints
│       ├── auth.py
│       ├── cases.py
│       ├── rules.py
│       ├── genai.py
│       ├── workflows.py
│       └── analytics.py
├── core/             # Core functionality
│   ├── config.py
│   └── security.py
├── models/           # Database models
│   └── base.py
├── schemas/          # Pydantic schemas
│   └── __init__.py
├── services/         # Business logic
│   ├── genai/
│   ├── drools/
│   ├── bpmn/
│   └── mq/
├── db/               # Database configuration
│   └── session.py
└── main.py           # Application entry point
```

## Default Users

- **Admin**: username: `admin`, password: `admin123`
- **Collector 1**: username: `collector1`, password: `admin123`
- **Collector 2**: username: `collector2`, password: `admin123`

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### Cases
- `GET /api/v1/cases` - List cases
- `GET /api/v1/cases/{id}` - Get case details
- `POST /api/v1/cases` - Create case
- `PATCH /api/v1/cases/{id}` - Update case
- `POST /api/v1/cases/{id}/assign` - Assign case

### GenAI
- `POST /api/v1/genai/summarize` - Generate case summary
- `POST /api/v1/genai/generate-script` - Generate collection script
- `POST /api/v1/genai/analyze-intent` - Analyze customer intent
- `POST /api/v1/genai/score-willingness` - Score payment willingness
- `POST /api/v1/genai/compliance-check` - Check script compliance

### Rules
- `GET /api/v1/rules` - List rules
- `POST /api/v1/rules` - Create rule
- `PUT /api/v1/rules/{id}` - Update rule
- `DELETE /api/v1/rules/{id}` - Delete rule

### Analytics
- `GET /api/v1/analytics/performance` - Performance metrics
- `GET /api/v1/analytics/compliance-metrics` - Compliance metrics
- `GET /api/v1/analytics/ab-test-results` - A/B test results
- `GET /api/v1/analytics/dashboard-stats` - Dashboard statistics

## Development

### Code Quality

```bash
# Format code
black app/

# Lint
ruff check app/

# Type checking
mypy app/
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## License

Proprietary - Capco
