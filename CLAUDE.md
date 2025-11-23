# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **ClickBank Affiliate Automation SaaS** platform - an AI-powered automation system for ClickBank affiliates. The platform helps users find profitable products, generate content using Claude AI, and automate their entire affiliate marketing funnel across multiple channels (WordPress, social media, email).

**Business Model:** Tiered SaaS ($49-$399/month) with limits based on tier (Starter/Professional/Agency).

## Architecture

**Monorepo structure** with separate backend (FastAPI) and frontend (React) applications:

```
backend/          # FastAPI Python backend
frontend/         # React TypeScript frontend
docs/            # Comprehensive documentation
.github/         # CI/CD workflows
docker-compose.yml
```

### Backend Architecture (FastAPI + PostgreSQL + Redis + Celery)

**Layered architecture:**
- `app/api/v1/` - API endpoint routers (auth, users, products, campaigns, content, workflows, analytics, webhooks, websocket)
- `app/models/` - SQLAlchemy ORM models (User, Product, Campaign, Content, Workflow, AnalyticsEvent, Bonus, Team, TeamMember)
- `app/schemas/` - Pydantic request/response schemas
- `app/services/` - Business logic and external integrations (Claude AI, ClickBank, Stripe, Email, WordPress, Social Media, S3 Storage)
- `app/core/` - Core utilities (security, cache, logging, exceptions)
- `app/tasks/` - Celery background tasks
- `app/db/` - Database session and base classes

**Key architectural patterns:**
- JWT authentication with access tokens (15 min) and refresh tokens (7 days)
- Async SQLAlchemy 2.0 for all database operations
- Service layer pattern for external integrations
- WebSocket support for real-time AI content streaming
- Background task processing with Celery for long-running operations

**Database:** PostgreSQL with UUID primary keys, JSONB for flexible data, and proper foreign key cascades.

### Frontend Architecture (React + TypeScript + Vite)

**State management strategy:**
- **Zustand** for global app state (auth, UI preferences)
- **TanStack Query** for server state, caching, and automatic refetching
- **React Router v6** for routing with protected routes

**Key patterns:**
- Automatic JWT token refresh via Axios interceptors in `services/api.ts`
- Protected routes check `authStore.isAuthenticated`
- Persistent auth state via Zustand persist middleware
- shadcn/ui components with Tailwind CSS

## Development Commands

### Initial Setup

```bash
# Clone and setup environment
git clone https://github.com/imnuman/affiliates_profit_-automator.git
cd affiliates_profit_-automator
cp .env.example .env
# Edit .env with required API keys (ANTHROPIC_API_KEY, DATABASE_URL, REDIS_URL, JWT_SECRET_KEY, SECRET_KEY)

# Start infrastructure with Docker
docker-compose up -d postgres redis
```

### Backend Development

```bash
cd backend

# Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Database migrations
alembic upgrade head                    # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
alembic downgrade -1                    # Rollback one migration

# Seed database with test data
python -m scripts.seed_data
# Creates test users: starter@test.com, pro@test.com, agency@test.com (all passwords: Password123!)

# Run development server
python -m app.main                      # API at http://localhost:8000
# Or with auto-reload:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# Run Celery beat scheduler (separate terminal)
celery -A app.tasks.celery_app beat --loglevel=info

# Run Celery Flower (monitoring UI)
celery -A app.tasks.celery_app flower  # http://localhost:5555

# Testing
pytest                                   # Run all tests
pytest tests/test_auth.py               # Run specific test file
pytest -k "test_login"                  # Run tests matching pattern
pytest --cov=app --cov-report=html      # Coverage report in htmlcov/
pytest -v -s                            # Verbose with print output

# Linting and formatting
black .                                  # Format code
isort .                                  # Sort imports
flake8 app/ --max-line-length=120 --extend-ignore=E203,W503
```

### Frontend Development

```bash
cd frontend

# Setup Node environment
npm install

# Development server
npm run dev                             # Dev server at http://localhost:5173

# Building
npm run build                           # Production build to dist/
npm run preview                         # Preview production build

# Linting
npm run lint                            # ESLint check
npm run lint:fix                        # Auto-fix issues

# Testing
npm test                                # Run tests (if configured)
```

### Docker Operations

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend          # Backend logs
docker-compose logs -f postgres         # Database logs

# Rebuild after changes
docker-compose up -d --build

# Stop all services
docker-compose down

# Reset everything (WARNING: deletes data)
docker-compose down -v
```

## Critical Implementation Details

### Authentication Flow

1. **Login:** `POST /api/v1/auth/login` returns `access_token` (15 min) and `refresh_token` (7 days)
2. **Token storage:** Frontend stores in Zustand with persistence to localStorage
3. **Automatic refresh:** Axios interceptor in `frontend/src/services/api.ts` catches 401 errors and calls `/api/v1/auth/refresh`
4. **Protected routes:** `PrivateRoute` component checks `authStore.isAuthenticated`
5. **Logout:** Clears tokens from both backend (Redis blacklist) and frontend store

### WebSocket Real-Time Streaming

**Endpoint:** `ws://localhost:8000/api/v1/ws/content/generate?token={jwt_token}`

Authentication via query parameter (WebSocket can't use headers). Send JSON messages:

```json
{
  "type": "blog_post",
  "campaign_id": "uuid",
  "prompt": "Write a review...",
  "title": "Product Review",
  "metadata": {}
}
```

Receive streaming chunks:
```json
{"type": "started", "content_id": "uuid"}
{"type": "chunk", "content": "text..."}
{"type": "complete", "content_id": "uuid"}
{"type": "error", "message": "..."}
```

### User Tier Limits

Defined in `backend/app/config.py` as `TIER_LIMITS`:
- **Starter:** 50 AI generations/month, 5 campaigns, 100 products
- **Professional:** 200 generations, 25 campaigns, 500 products
- **Agency:** Unlimited (99999)

Check limits in endpoint logic before allowing operations.

### Database Models Key Relationships

- **User** → Campaigns → Content (cascade delete)
- **User** → Workflows (cascade delete)
- **Campaign** → Product (SET NULL on product delete)
- **Campaign** → Analytics Events (cascade delete)
- **Team** → TeamMembers (cascade delete, unique constraint on team_id + user_id)

All models use UUID primary keys. Timestamps are UTC with `server_default=now()`.

### Service Layer Pattern

External integrations are isolated in `app/services/`:
- `claude.py` - Anthropic API for content generation (streaming support)
- `clickbank.py` - ClickBank API for product data
- `stripe.py` - Payment processing and subscriptions
- `email.py` - Postmark for transactional emails
- `wordpress.py` - XML-RPC for WordPress publishing
- `social_media.py` - Twitter/Facebook/LinkedIn posting
- `storage.py` - AWS S3 file uploads and presigned URLs

Always use service classes instead of calling APIs directly in endpoints. Services handle errors and return consistent exceptions.

### Celery Background Tasks

Defined in `app/tasks/`:
- `content_tasks.py` - AI content generation, batch processing
- `clickbank_tasks.py` - Product data sync, daily updates
- `workflow_tasks.py` - Execute automation workflows
- `email_tasks.py` - Send bulk emails, drip campaigns

**Scheduled tasks** (Celery Beat) in `app/tasks/celery_app.py`:
- Product sync: daily at 2 AM UTC
- Workflow execution: every 15 minutes
- Analytics aggregation: hourly

Trigger manually: `task_name.delay(arg1, arg2)`

### Environment Variables Requirements

**Minimum required for development:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET_KEY` - Random secret for JWT signing
- `SECRET_KEY` - App secret key
- `ANTHROPIC_API_KEY` - Claude AI API key

**Optional but recommended:**
- `STRIPE_SECRET_KEY` - For payment testing
- `CLICKBANK_API_KEY` - For product data
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME` - For file uploads

See `.env.example` for complete list.

## API Documentation

- **Interactive Docs:** http://localhost:8000/docs (Swagger UI)
- **ReDoc:** http://localhost:8000/redoc
- **Full API docs:** See `docs/API_DOCUMENTATION.md`

## Common Issues and Solutions

**"Table does not exist" errors:**
- Run `alembic upgrade head` to apply migrations
- Check `DATABASE_URL` points to correct database

**JWT decode errors:**
- Ensure `JWT_SECRET_KEY` matches between backend restarts
- Clear frontend localStorage to remove stale tokens

**Celery tasks not running:**
- Verify Redis is running: `redis-cli ping` should return `PONG`
- Check `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` in `.env`
- Ensure Celery worker is running

**WebSocket connection fails:**
- Pass JWT token as query parameter, not in headers
- Token must be valid access token (not expired)

**CORS errors in development:**
- Backend `CORS_ORIGINS` in config must include `http://localhost:5173`
- Check `frontend/vite.config.ts` proxy configuration

## Testing Workflow

**Backend tests** use pytest with async support:
- Fixtures in `tests/conftest.py` provide test database and client
- Use `async def test_*` for async tests
- Mark with `@pytest.mark.asyncio`

**Frontend tests** use Vitest (if configured):
- Test files: `*.test.tsx` or `*.spec.tsx`
- Mock API calls with MSW or similar

## Deployment

**GitHub Actions workflows:**
- `.github/workflows/ci.yml` - Runs on PR to main/develop (tests, linting, Docker build)
- `.github/workflows/deploy-staging.yml` - Auto-deploy develop branch to staging
- `.github/workflows/deploy-production.yml` - Manual approval for main branch to production

**Production environment:** AWS ECS with RDS PostgreSQL and ElastiCache Redis.

See `docs/DEPLOYMENT.md` for detailed deployment instructions.

## Key Files to Understand

- `backend/app/main.py` - FastAPI application entry point, CORS, router registration
- `backend/app/api/v1/router.py` - Central router that includes all endpoint routers
- `backend/app/dependencies.py` - Dependency injection (DB session, current user)
- `backend/app/config.py` - All environment variables and tier limits
- `backend/app/database.py` - Database engine and session factory
- `frontend/src/App.tsx` - Route configuration and protected routes
- `frontend/src/services/api.ts` - Axios client with auth interceptors
- `frontend/src/store/authStore.ts` - Authentication state management
- `docker-compose.yml` - Local development infrastructure
