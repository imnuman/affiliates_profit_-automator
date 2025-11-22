# Development Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** & **Docker Compose** (v2.0+)
- **Python** 3.11+ (for local backend development)
- **Node.js** 18+ (for local frontend development)
- **Git**
- **PostgreSQL** 15+ (optional, can use Docker)
- **Redis** 7+ (optional, can use Docker)

## Quick Start with Docker

The fastest way to get started:

```bash
# 1. Clone the repository
git clone https://github.com/imnuman/affiliates_profit_-automator.git
cd affiliates_profit_-automator

# 2. Copy environment variables
cp .env.example .env

# 3. Edit .env with your API keys
nano .env  # or use your preferred editor

# 4. Start all services
docker-compose up -d

# 5. Run database migrations
docker-compose exec backend alembic upgrade head

# 6. Create test user (optional)
docker-compose exec backend python -m app.db.init_db
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs
- Celery Flower: http://localhost:5555

## Local Development (Without Docker)

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Set up environment variables
cp ../.env.example ../.env
# Edit .env with your configuration

# 5. Start PostgreSQL and Redis
# Option A: Using Docker
docker-compose up -d postgres redis

# Option B: Using local installations
# Make sure PostgreSQL and Redis are running

# 6. Run database migrations
alembic upgrade head

# 7. Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 8. In another terminal, start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# 9. In another terminal, start Celery beat
celery -A app.tasks.celery_app beat --loglevel=info
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# The frontend will be available at http://localhost:5173
```

## Environment Variables

### Required Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/clickbank_saas

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# JWT
JWT_SECRET_KEY=your-secret-key-here-change-in-production
SECRET_KEY=your-app-secret-key

# Anthropic (Claude AI)
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Optional Variables

```bash
# ClickBank (for product sync)
CLICKBANK_API_KEY=your-clickbank-api-key
CLICKBANK_DEVELOPER_KEY=your-clickbank-developer-key

# Stripe (for payments)
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Email (for notifications)
POSTMARK_API_KEY=your-postmark-api-key
SENDGRID_API_KEY=your-sendgrid-api-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

## Database Setup

### Create Database

```bash
# Using psql
psql -U postgres
CREATE DATABASE clickbank_saas;
\q
```

### Run Migrations

```bash
cd backend
alembic upgrade head
```

### Create Migration

```bash
# After modifying models
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Seed Test Data

```bash
python -m app.db.init_db
```

This creates a test user:
- Email: `admin@test.com`
- Password: `admin123`

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_auth.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## Code Quality

### Backend

```bash
cd backend

# Format code with Black
black .

# Sort imports
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy app/
```

### Frontend

```bash
cd frontend

# Lint
npm run lint

# Format
npm run format

# Type check
npm run type-check
```

## Debugging

### Backend Debugging

Use VS Code debugger with this `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

### Frontend Debugging

React DevTools browser extension is recommended.

## Useful Commands

### Docker

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart service
docker-compose restart backend

# Rebuild service
docker-compose up -d --build backend

# Stop all services
docker-compose down

# Clean up (remove volumes)
docker-compose down -v
```

### Database

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d clickbank_saas

# Create backup
docker-compose exec postgres pg_dump -U postgres clickbank_saas > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres clickbank_saas < backup.sql
```

### Celery

```bash
# Purge all tasks
celery -A app.tasks.celery_app purge

# Inspect active tasks
celery -A app.tasks.celery_app inspect active

# Monitor with Flower
# Visit http://localhost:5555
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

### Frontend Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Migration Errors

```bash
# Rollback migration
alembic downgrade -1

# Drop all tables and recreate
alembic downgrade base
alembic upgrade head
```

## IDE Setup

### VS Code Extensions

Recommended extensions:
- Python
- Pylance
- ES Lint
- Prettier
- Docker
- GitLens
- Thunder Client (API testing)

### PyCharm

Configure Python interpreter to use `backend/venv`.

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- Review [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for database structure
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

## Getting Help

- Check existing issues on GitHub
- Review documentation in `docs/` folder
- Ask in Discord community
