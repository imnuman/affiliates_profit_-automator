# 🚀 Quick Start Guide - MVP Setup

This guide will help you get the ClickBank Affiliate SaaS MVP running locally in **under 10 minutes**.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

## Option 1: Automated Setup (Recommended)

```bash
# Run the automated setup script
./setup-mvp.sh
```

This script will:
- Install PostgreSQL and Redis (if not present)
- Create the database
- Configure authentication
- Start services

## Option 2: Manual Setup

### 1. Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib redis-server
sudo systemctl start postgresql redis-server
```

**macOS:**
```bash
brew install postgresql@15 redis
brew services start postgresql@15
brew services start redis
```

### 2. Create Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In psql:
CREATE DATABASE clickbank_saas;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE clickbank_saas TO postgres;
\q
```

### 3. Configure PostgreSQL for Password Auth

Edit `/etc/postgresql/*/main/pg_hba.conf`:
```
# Change 'peer' to 'md5' for local connections
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## 🔧 Backend Setup

### 1. Install Python Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file is already created. **You just need to add your DeepSeek API key:**

```bash
# Edit .env and set:
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema
```

### 4. Seed Test Data (Optional but Recommended)

```bash
python -m scripts.seed_data
```

This creates 3 test users:
- `starter@test.com` / `Password123!` (Starter tier)
- `pro@test.com` / `Password123!` (Professional tier)
- `agency@test.com` / `Password123!` (Agency tier)

### 5. Start Backend Server

```bash
# Method 1: Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using Python module
python -m app.main
```

Backend will be available at:
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### 6. Start Celery Worker (Optional - for background tasks)

In a new terminal:
```bash
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info
```

### 7. Start Celery Beat (Optional - for scheduled tasks)

In another terminal:
```bash
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app beat --loglevel=info
```

## 🎨 Frontend Setup

### 1. Install Node Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Frontend will be available at:
- **App:** http://localhost:5173

## ✅ Verify Everything Works

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "app": "ClickBank Affiliate SaaS",
  "version": "v1",
  "environment": "development"
}
```

### 2. Test API Documentation

Open http://localhost:8000/docs in your browser

### 3. Test Frontend

1. Open http://localhost:5173
2. Click "Sign Up"
3. Create an account or use test credentials:
   - Email: `pro@test.com`
   - Password: `Password123!`

### 4. Test AI Content Generation

1. Log in to the frontend
2. Navigate to "Content"
3. Click "Generate Content"
4. Select content type and enter a prompt
5. Click "Generate Content"

You should see AI-generated content from DeepSeek!

## 🧪 Run Tests

```bash
cd backend
pytest
```

For coverage report:
```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## 🌐 Access from Public IP

If your machine has a public IP and you want to access it remotely:

### 1. Update CORS Settings

Edit `.env`:
```bash
CORS_ORIGINS=["http://localhost:5173", "http://YOUR_PUBLIC_IP:5173", "http://YOUR_PUBLIC_IP:8000"]
FRONTEND_URL=http://YOUR_PUBLIC_IP:5173
```

### 2. Start with 0.0.0.0

Backend (already configured):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:
```bash
npm run dev -- --host 0.0.0.0
```

### 3. Configure Firewall

```bash
# Allow ports 8000 (backend) and 5173 (frontend)
sudo ufw allow 8000
sudo ufw allow 5173
```

Now access:
- Backend API: http://YOUR_PUBLIC_IP:8000
- Frontend: http://YOUR_PUBLIC_IP:5173

## 🐛 Troubleshooting

### Database Connection Error

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql

# Check if database exists
sudo -u postgres psql -l | grep clickbank_saas
```

### Redis Connection Error

**Error:** `Error connecting to Redis`

**Solution:**
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Start if not running
sudo systemctl start redis-server

# Test connection
redis-cli ping  # Should return PONG
```

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### AI API Error

**Error:** `Error generating content` or `401 Unauthorized`

**Solution:**
1. Check your DeepSeek API key in `.env`
2. Verify the key is valid
3. Check API quota/limits

### CORS Error in Frontend

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
Edit `.env` and add your frontend URL to `CORS_ORIGINS`:
```bash
CORS_ORIGINS=["http://localhost:5173", "http://YOUR_IP:5173"]
```

Restart backend server.

## 📊 What's Working in MVP

✅ User authentication (signup, login, logout)
✅ AI content generation with DeepSeek
✅ Content management (create, view, delete)
✅ Campaign management
✅ Analytics dashboard
✅ Settings and profile management
✅ File uploads (if AWS S3 configured)
✅ Real-time WebSocket streaming

## 🚧 What's Mock/Optional for MVP

⚠️ ClickBank product sync (optional - can use mock data)
⚠️ Stripe payments (optional - tier limits work without payment)
⚠️ Email sending (optional - user can test without email)
⚠️ WordPress publishing (optional - requires WordPress site)
⚠️ Social media posting (optional - requires social accounts)

## 📝 Next Steps

1. **Test the AI functionality** - Generate blog posts, emails, etc.
2. **Explore the dashboard** - Check analytics and metrics
3. **Create campaigns** - Set up affiliate campaigns
4. **Customize** - Modify prompts, add features
5. **Deploy** - When ready, deploy to AWS/production

## 🆘 Need Help?

1. Check the logs:
   - Backend: Terminal where uvicorn is running
   - Frontend: Browser console (F12)
   - Celery: Terminal where worker is running

2. Check documentation:
   - `docs/ARCHITECTURE.md` - System architecture
   - `docs/API_DOCUMENTATION.md` - API endpoints
   - `docs/DATABASE_SCHEMA.md` - Database structure

3. Check `CLAUDE.md` for AI assistant guidance

## 🎉 Success!

If you can:
- Log in to the frontend
- See the dashboard
- Generate AI content
- View analytics

**You're ready to go! The MVP is working!** 🚀
