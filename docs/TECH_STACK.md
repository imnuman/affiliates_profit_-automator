# Technology Stack

## Backend

### Core Framework
- **FastAPI 0.109.0** - Modern Python web framework
  - Async/await support
  - Automatic API documentation
  - Fast performance (based on Starlette and Pydantic)
  - Built-in dependency injection

### Language
- **Python 3.11+** - Latest Python with performance improvements

### Database
- **PostgreSQL 15+** - Primary data store
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **asyncpg** - Async PostgreSQL driver

### Caching & Queuing
- **Redis 7.2** - Caching and session storage
- **Celery 5.3** - Distributed task queue
- **Flower** - Celery monitoring UI

### Authentication & Security
- **python-jose** - JWT token generation/validation
- **passlib[bcrypt]** - Password hashing
- **slowapi** - Rate limiting

### External APIs
- **Anthropic Claude API** - AI content generation
- **Stripe API** - Payment processing
- **ClickBank API** - Product data
- **Postmark** - Transactional emails
- **SendGrid** - Marketing emails

### Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage
- **faker** - Test data generation

### Code Quality
- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking

---

## Frontend

### Core Framework
- **React 18** - UI library
- **TypeScript 5.3** - Type-safe JavaScript
- **Vite 5.0** - Build tool and dev server

### Styling
- **Tailwind CSS 3.4** - Utility-first CSS
- **shadcn/ui** - Component library
- **Radix UI** - Headless UI components
- **class-variance-authority** - Component variants
- **tailwind-merge** - Utility merging
- **lucide-react** - Icon library

### State Management
- **Zustand 4.5** - Lightweight state management
- **TanStack Query 5.20** - Server state management
- **React Hook Form 7.50** - Form handling
- **Zod 3.22** - Schema validation

### Routing & Navigation
- **React Router 6.22** - Client-side routing

### HTTP & Real-time
- **Axios 1.6** - HTTP client
- **Socket.IO Client 4.7** - WebSocket client

### Development Tools
- **ESLint** - JavaScript linting
- **Prettier** - Code formatting
- **Vitest** - Unit testing
- **Testing Library** - Component testing

---

## Infrastructure

### Cloud Platform
- **AWS** - Primary cloud provider
  - ECS (Elastic Container Service)
  - RDS (Relational Database Service)
  - ElastiCache (Redis)
  - S3 (Object Storage)
  - CloudFront (CDN)
  - Route53 (DNS)
  - ACM (SSL Certificates)
  - Secrets Manager
  - CloudWatch (Logging/Monitoring)

### Infrastructure as Code
- **Terraform** - Infrastructure provisioning
- **Docker** - Containerization
- **Docker Compose** - Local development

### CI/CD
- **GitHub Actions** - Continuous integration/deployment
- **GitHub Container Registry** - Docker image storage

### Monitoring & Logging
- **Sentry** - Error tracking
- **CloudWatch** - AWS metrics and logs
- **Better Stack** - Log aggregation
- **Celery Flower** - Task monitoring

---

## Development Tools

### Version Control
- **Git** - Source control
- **GitHub** - Repository hosting

### API Development
- **Swagger UI** - API documentation (built into FastAPI)
- **ReDoc** - Alternative API docs
- **Postman/Thunder Client** - API testing

### Database Tools
- **pgAdmin** - PostgreSQL GUI
- **DBeaver** - Universal database tool
- **Redis CLI** - Redis command-line

### Code Editors
- **VS Code** - Recommended IDE
- **PyCharm** - Alternative for Python
- **WebStorm** - Alternative for JavaScript

---

## Package Managers

- **pip** - Python package manager
- **npm** - Node.js package manager
- **Docker** - Container management

---

## Performance

### Backend Performance
- **Uvicorn** - ASGI server
- **Async/await** - Non-blocking I/O
- **Connection pooling** - Database optimization
- **Redis caching** - Query caching

### Frontend Performance
- **Code splitting** - Lazy loading
- **Tree shaking** - Dead code elimination
- **Minification** - Reduced bundle size
- **CDN delivery** - Fast global access

---

## Security

- **JWT** - Stateless authentication
- **Bcrypt** - Password hashing
- **HTTPS/TLS** - Encrypted communication
- **CORS** - Cross-origin protection
- **Rate limiting** - Abuse prevention
- **SQL injection** - ORM protection
- **XSS protection** - Input sanitization

---

## Why These Technologies?

### FastAPI over Django/Flask
- Modern async support
- Automatic API docs
- Better performance
- Type safety with Pydantic

### React over Vue/Angular
- Larger ecosystem
- Better component library support
- Strong TypeScript integration
- Industry standard

### PostgreSQL over MySQL/MongoDB
- Advanced features (JSONB, full-text search)
- ACID compliance
- Better for complex queries
- Mature ecosystem

### Tailwind over Bootstrap/Material-UI
- Utility-first approach
- Better customization
- Smaller bundle size
- Modern design patterns

### TanStack Query over Redux
- Built for async data
- Automatic caching
- Less boilerplate
- Better dev experience

---

## Version Requirements

### Minimum Versions
- Python: 3.11+
- Node.js: 18+
- PostgreSQL: 15+
- Redis: 7+
- Docker: 20+

### Browser Support
- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Mobile browsers: Last 2 versions

---

This stack is chosen for:
- **Developer Experience** - Modern tooling, great DX
- **Performance** - Fast runtime, efficient builds
- **Scalability** - Handles growth easily
- **Maintainability** - Clean code, good practices
- **Community** - Strong ecosystem, active development
