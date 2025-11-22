# Architecture Overview

## System Architecture

The ClickBank Affiliate SaaS platform follows a **microservices-inspired architecture** with a clear separation between frontend, backend, and background processing layers.

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser    │  │    Mobile    │  │  Desktop App │          │
│  │  (React SPA) │  │   (Future)   │  │   (Future)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CDN / LOAD BALANCER                      │
│                      (CloudFront + ALB)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
┌───────────────────────────┐   ┌──────────────────────────┐
│    FRONTEND TIER          │   │     BACKEND TIER         │
│  ┌─────────────────────┐  │   │  ┌────────────────────┐  │
│  │   React App         │  │   │  │  FastAPI Server    │  │
│  │   - SPA (Vite)      │  │   │  │  - REST API        │  │
│  │   - TypeScript      │  │   │  │  - WebSocket       │  │
│  │   - Tailwind CSS    │  │   │  │  - Authentication  │  │
│  │   - React Router    │  │   │  │  - Authorization   │  │
│  └─────────────────────┘  │   │  └────────────────────┘  │
│  (Nginx Container)        │   │  (Uvicorn Container)     │
└───────────────────────────┘   └──────────────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
        ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
        │   DATABASE TIER     │ │    CACHE TIER       │ │   TASK QUEUE        │
        │  ┌───────────────┐  │ │  ┌───────────────┐  │ │  ┌───────────────┐  │
        │  │  PostgreSQL   │  │ │  │    Redis      │  │ │  │  Celery       │  │
        │  │  - Tables     │  │ │  │  - Cache      │  │ │  │  - Workers    │  │
        │  │  - Indexes    │  │ │  │  - Sessions   │  │ │  │  - Beat       │  │
        │  │  - Relations  │  │ │  │  - Queue      │  │ │  │  - Flower     │  │
        │  └───────────────┘  │ │  └───────────────┘  │ │  └───────────────┘  │
        │  (RDS/Container)    │ │  (ElastiCache/      │ │  (Container)        │
        │                     │ │   Container)        │ │                     │
        └─────────────────────┘ └─────────────────────┘ └─────────────────────┘
                    │
                    ▼
        ┌─────────────────────────────────────────────┐
        │         EXTERNAL SERVICES                    │
        │  ┌────────────┐  ┌──────────┐  ┌─────────┐  │
        │  │  Anthropic │  │ ClickBank│  │ Stripe  │  │
        │  │  (Claude)  │  │   API    │  │   API   │  │
        │  └────────────┘  └──────────┘  └─────────┘  │
        │  ┌────────────┐  ┌──────────┐  ┌─────────┐  │
        │  │  Postmark  │  │ SendGrid │  │   AWS   │  │
        │  │   Email    │  │  Email   │  │   S3    │  │
        │  └────────────┘  └──────────┘  └─────────┘  │
        └─────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer (React + TypeScript)

**Technology Stack:**
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite (fast HMR, optimized builds)
- **Styling:** Tailwind CSS + shadcn/ui components
- **State Management:**
  - Zustand (global state: auth, UI)
  - TanStack Query (server state, caching)
- **Routing:** React Router v6
- **HTTP Client:** Axios with interceptors
- **Real-time:** Socket.IO client

**Key Features:**
- Single Page Application (SPA)
- Protected routes with JWT authentication
- Automatic token refresh
- Responsive design (mobile-first)
- Dark mode support
- Optimistic UI updates
- Error boundaries

**File Structure:**
```
frontend/src/
├── components/
│   ├── ui/           # Reusable UI components
│   └── layout/       # Layout components
├── pages/            # Route pages
├── services/         # API clients
├── hooks/            # Custom React hooks
├── store/            # Zustand stores
├── lib/              # Utilities
└── styles/           # Global styles
```

---

### Backend Layer (FastAPI + Python)

**Technology Stack:**
- **Framework:** FastAPI (async, high-performance)
- **Language:** Python 3.11+
- **ORM:** SQLAlchemy 2.0 (async)
- **Validation:** Pydantic v2
- **Authentication:** JWT (python-jose)
- **Task Queue:** Celery
- **ASGI Server:** Uvicorn

**Architecture Pattern:** Layered Architecture

```
┌─────────────────────────────────────┐
│         API Layer (Routes)          │
│  - Request validation               │
│  - Response serialization           │
│  - Error handling                   │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│       Business Logic (Services)     │
│  - ClickBank integration            │
│  - Claude AI content generation     │
│  - Stripe payment processing        │
│  - Email sending                    │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│       Data Access Layer (Models)    │
│  - SQLAlchemy ORM models            │
│  - Database queries                 │
│  - Migrations (Alembic)             │
└─────────────────────────────────────┘
```

**File Structure:**
```
backend/app/
├── api/v1/          # API endpoints
├── models/          # Database models
├── schemas/         # Pydantic schemas
├── services/        # Business logic
├── tasks/           # Celery tasks
├── core/            # Core utilities
├── db/              # Database config
└── utils/           # Helper functions
```

**API Versioning:**
- `/api/v1/` - Current version
- Future versions can coexist: `/api/v2/`

---

### Database Layer (PostgreSQL)

**Database Design:**
- **RDBMS:** PostgreSQL 15+
- **Connection:** Async (asyncpg)
- **Migrations:** Alembic
- **Pooling:** SQLAlchemy async pool

**Tables:**
1. `users` - User accounts
2. `products` - ClickBank products
3. `campaigns` - Affiliate campaigns
4. `content` - Generated content
5. `workflows` - Automation workflows
6. `analytics_events` - Tracking events
7. `bonuses` - Bonus delivery
8. `teams` - Team management
9. `team_members` - Team membership

**Indexes:**
- Primary keys (UUID)
- Foreign keys
- Search indexes (email, clickbank_id)
- Composite indexes for analytics queries

**Performance:**
- Query caching in Redis
- Materialized views for complex analytics
- Partitioning for analytics_events (by date)

---

### Cache Layer (Redis)

**Use Cases:**
1. **Session Storage** - User sessions
2. **Query Caching** - Expensive database queries
3. **Rate Limiting** - API rate limits per user
4. **Task Queue** - Celery broker & backend
5. **Real-time Data** - WebSocket connections

**TTL Strategy:**
- User sessions: 7 days
- Query cache: 5-60 minutes
- Product data: 1 hour
- Analytics: 15 minutes

---

### Background Processing (Celery)

**Task Types:**

1. **Periodic Tasks (Beat):**
   - Sync ClickBank products (hourly)
   - Process scheduled content (15 min)
   - Send scheduled emails (15 min)
   - Generate daily insights (3 AM)
   - Database backups (4 AM)

2. **On-Demand Tasks:**
   - AI content generation
   - Email sending
   - WordPress publishing
   - Social media posting
   - Analytics processing

**Queue Strategy:**
- Default queue: General tasks
- Priority queue: User-facing tasks
- Slow queue: Long-running tasks (AI generation)

**Monitoring:**
- Celery Flower dashboard
- Task success/failure metrics
- Queue depth monitoring

---

## Data Flow

### Request Flow (API Call)

```
1. Client sends HTTP request
   ↓
2. API Gateway / Load Balancer
   ↓
3. FastAPI receives request
   ↓
4. JWT validation (if protected)
   ↓
5. Request validation (Pydantic)
   ↓
6. Check cache (Redis)
   ├─ Hit → Return cached data
   └─ Miss → Continue
   ↓
7. Business logic (Service layer)
   ↓
8. Database query (PostgreSQL)
   ↓
9. Cache result (Redis)
   ↓
10. Response serialization
   ↓
11. Return to client
```

### Background Task Flow

```
1. API endpoint queues task
   ↓
2. Celery worker picks up task
   ↓
3. Task executes (e.g., AI generation)
   ↓
4. Result stored in database
   ↓
5. Notification sent (WebSocket/Email)
   ↓
6. Task marked complete
```

### Real-time Content Generation

```
1. User clicks "Generate Content"
   ↓
2. Frontend opens WebSocket connection
   ↓
3. Backend calls Claude API
   ↓
4. Claude streams response chunks
   ↓
5. Backend forwards chunks to WebSocket
   ↓
6. Frontend displays in real-time
   ↓
7. Content saved to database when complete
```

---

## Security Architecture

### Authentication Flow

```
1. User submits credentials
   ↓
2. Backend validates credentials
   ↓
3. Generate JWT tokens:
   - Access token (15 min)
   - Refresh token (7 days)
   ↓
4. Store refresh token hash in DB
   ↓
5. Return tokens to client
   ↓
6. Client stores in memory + localStorage
   ↓
7. Include access token in API requests
   ↓
8. When expired, use refresh token
```

### Security Layers

1. **Network:** TLS 1.3, HTTPS only
2. **Application:** JWT validation, rate limiting
3. **Data:** Encryption at rest, bcrypt hashing
4. **Infrastructure:** VPC, security groups, WAF

---

## Scalability Strategy

### Horizontal Scaling

- **Frontend:** Static files on CDN
- **Backend:** Multiple FastAPI instances (ECS)
- **Database:** Read replicas for queries
- **Celery:** Multiple worker instances
- **Redis:** Redis Cluster for sharding

### Vertical Scaling

- **Database:** Increase instance size
- **Cache:** More memory
- **Workers:** More CPU/memory

### Database Optimization

- Connection pooling
- Query optimization
- Index tuning
- Partitioning large tables

---

## Monitoring & Observability

### Metrics Collection

- **Application:** Sentry (errors)
- **Infrastructure:** CloudWatch (AWS)
- **Logs:** Better Stack (centralized)
- **APM:** Response times, throughput
- **Custom:** Business metrics (conversions, revenue)

### Alerting

- API error rate > 1%
- Response time > 500ms (p95)
- Database CPU > 80%
- Queue depth > 1000
- Failed tasks > 10%

---

## Disaster Recovery

### Backup Strategy

- **Database:** Daily backups, 30-day retention
- **Configuration:** Version control (Git)
- **Secrets:** AWS Secrets Manager
- **Logs:** S3 archive (90 days)

### Recovery Plan

- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 1 hour
- Multi-AZ deployment for HA
- Automated failover

---

This architecture is designed for:
- **Performance:** < 200ms API response time
- **Scalability:** Support 1,000+ concurrent users
- **Reliability:** 99.9% uptime
- **Maintainability:** Clear separation of concerns
- **Security:** Defense in depth
