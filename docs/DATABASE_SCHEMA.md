# Database Schema

## Overview

The database schema is designed using PostgreSQL 15+ with the following principles:
- **UUID primary keys** for distributed systems and security
- **Timestamps** on all tables (created_at, updated_at)
- **JSONB columns** for flexible metadata storage
- **Indexes** optimized for common queries
- **Foreign keys** with appropriate cascade rules

## Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    users    │────────>│  campaigns   │────────>│   content   │
└─────────────┘         └──────────────┘         └─────────────┘
       │                       │
       │                       │
       │                       ▼
       │                ┌──────────────┐
       │                │   products   │
       │                └──────────────┘
       │
       ▼
┌─────────────┐         ┌──────────────┐
│  workflows  │         │   analytics  │
└─────────────┘         │    _events   │
                        └──────────────┘
       │
       ▼
┌─────────────┐         ┌──────────────┐
│   teams     │────────>│team_members  │
└─────────────┘         └──────────────┘
```

---

## Tables

### 1. users

Stores user account information and subscription details.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    tier VARCHAR(50) NOT NULL DEFAULT 'starter',  -- starter, professional, agency
    status VARCHAR(50) NOT NULL DEFAULT 'trial',   -- trial, active, suspended, canceled
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    is_email_verified BOOLEAN DEFAULT FALSE,
    trial_ends_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_tier ON users(tier);
```

**Columns:**
- `id`: Unique user identifier
- `email`: User's email address (login identifier)
- `password_hash`: Bcrypt hashed password
- `full_name`: User's display name
- `tier`: Subscription tier (starter/professional/agency)
- `status`: Account status
- `stripe_customer_id`: Stripe customer reference
- `stripe_subscription_id`: Stripe subscription reference
- `is_email_verified`: Email verification status
- `trial_ends_at`: When free trial expires

---

### 2. products

ClickBank product catalog with gravity metrics.

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clickbank_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    vendor VARCHAR(255) NOT NULL,
    category VARCHAR(255),
    description TEXT,
    commission_rate DECIMAL(5, 2),        -- Percentage (e.g., 75.00)
    commission_amount DECIMAL(10, 2),     -- Dollar amount per sale
    initial_sale_amount DECIMAL(10, 2),   -- Initial sale price
    gravity DECIMAL(10, 2),                -- ClickBank gravity score
    refund_rate DECIMAL(5, 2),             -- Refund percentage
    rebill BOOLEAN DEFAULT FALSE,          -- Has recurring billing
    popularity_rank INTEGER,
    data_snapshot JSONB,                   -- Full API response
    last_updated TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_products_clickbank_id ON products(clickbank_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_gravity ON products(gravity DESC);
CREATE INDEX idx_products_commission ON products(commission_amount DESC);
```

**Columns:**
- `clickbank_id`: ClickBank's product identifier
- `gravity`: Product popularity (higher = more affiliates making sales)
- `commission_rate`: Percentage commission
- `commission_amount`: Dollar amount per sale
- `refund_rate`: Refund percentage (lower is better)
- `rebill`: Whether product has recurring payments
- `data_snapshot`: Full ClickBank API response (JSONB)

---

### 3. campaigns

User's affiliate marketing campaigns.

```sql
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',  -- draft, active, paused, completed
    funnel_type VARCHAR(100),                     -- review, comparison, bonus, vsl, webinar
    affiliate_link TEXT,
    tracking_id VARCHAR(50) UNIQUE,
    settings JSONB,                               -- Campaign configuration
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_product_id ON campaigns(product_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_tracking_id ON campaigns(tracking_id);
```

**Columns:**
- `user_id`: Campaign owner
- `product_id`: Associated ClickBank product
- `name`: Campaign name
- `status`: Current campaign state
- `funnel_type`: Type of marketing funnel
- `tracking_id`: Unique tracking identifier
- `settings`: Custom campaign settings (JSONB)

---

### 4. content

AI-generated and user-created content.

```sql
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,                    -- blog_post, email, social_post, video_script, ad_copy
    title VARCHAR(500),
    body TEXT NOT NULL,
    metadata JSONB,                               -- Additional content data
    status VARCHAR(50) NOT NULL DEFAULT 'draft',  -- draft, published, scheduled, archived
    published_at TIMESTAMPTZ,
    scheduled_for TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_content_user_id ON content(user_id);
CREATE INDEX idx_content_campaign_id ON content(campaign_id);
CREATE INDEX idx_content_type ON content(type);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_scheduled ON content(scheduled_for) WHERE scheduled_for IS NOT NULL;
```

**Columns:**
- `type`: Content type (blog_post, email, etc.)
- `body`: Main content text
- `metadata`: SEO data, images, etc. (JSONB)
- `status`: Publishing status
- `scheduled_for`: When to auto-publish

---

### 5. workflows

Automation workflows for campaigns.

```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    trigger_type VARCHAR(100) NOT NULL,           -- manual, scheduled, event
    trigger_config JSONB,                         -- Trigger parameters
    actions JSONB NOT NULL,                       -- List of actions to execute
    conditions JSONB,                             -- Conditions to check
    status VARCHAR(50) NOT NULL DEFAULT 'draft',  -- draft, active, paused
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_next_run ON workflows(next_run_at) WHERE next_run_at IS NOT NULL;
```

**Columns:**
- `trigger_type`: How workflow is triggered
- `trigger_config`: Trigger parameters (JSONB)
- `actions`: Array of actions (JSONB)
- `conditions`: Execution conditions (JSONB)
- `next_run_at`: Next scheduled execution

---

### 6. analytics_events

Tracking events (clicks, conversions, refunds).

```sql
CREATE TABLE analytics_events (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,              -- click, conversion, refund, rebill
    source VARCHAR(255),                          -- Traffic source
    metadata JSONB,                               -- Event details
    revenue DECIMAL(10, 2),                       -- Revenue amount (for conversions)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analytics_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_campaign_id ON analytics_events(campaign_id);
CREATE INDEX idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_created_at ON analytics_events(created_at);
CREATE INDEX idx_analytics_composite ON analytics_events(user_id, campaign_id, event_type, created_at);
```

**Note:** This table grows rapidly. Consider partitioning by date for performance.

**Columns:**
- `event_type`: Type of event (click/conversion/refund)
- `source`: Where traffic came from
- `metadata`: Additional event data (JSONB)
- `revenue`: Dollar amount (for conversions)

**Partitioning Strategy (Future):**
```sql
-- Partition by month
CREATE TABLE analytics_events_2025_01 PARTITION OF analytics_events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

---

### 7. bonuses

Bonus products delivered to customers.

```sql
CREATE TABLE bonuses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    file_url VARCHAR(500),                        -- S3 URL or external link
    delivery_method VARCHAR(50) DEFAULT 'email',  -- email, download
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    delivered_count INTEGER DEFAULT 0,
    last_delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bonuses_campaign_id ON bonuses(campaign_id);
CREATE INDEX idx_bonuses_is_active ON bonuses(is_active);
```

**Columns:**
- `file_url`: Location of bonus file (S3)
- `delivery_method`: How bonus is delivered
- `delivered_count`: Number of times delivered

---

### 8. teams

Team/agency workspaces (Agency tier).

```sql
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    settings JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_teams_owner_id ON teams(owner_id);
CREATE INDEX idx_teams_is_active ON teams(is_active);
```

---

### 9. team_members

Team membership and roles.

```sql
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',  -- owner, admin, member, viewer
    permissions JSONB,                           -- Custom permissions
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);
```

---

## Relationships

### One-to-Many Relationships

1. **users → campaigns** (A user can have many campaigns)
2. **users → content** (A user can create many content pieces)
3. **users → workflows** (A user can create many workflows)
4. **campaigns → content** (A campaign can have many content pieces)
5. **campaigns → analytics_events** (A campaign has many tracking events)
6. **campaigns → bonuses** (A campaign can have many bonuses)
7. **teams → team_members** (A team has many members)

### Many-to-One Relationships

1. **campaigns → products** (Many campaigns can promote one product)
2. **team_members → users** (A user can be in multiple teams)

---

## Data Types

### Standard Types
- `UUID`: Primary keys, foreign keys
- `VARCHAR`: Text with max length
- `TEXT`: Unlimited text
- `DECIMAL`: Precise numbers (money, percentages)
- `INTEGER`: Whole numbers
- `BOOLEAN`: True/false
- `TIMESTAMPTZ`: Timestamp with timezone

### Special Types
- `JSONB`: Flexible metadata storage (indexed, queryable)
- `BIGSERIAL`: Auto-incrementing big integer (analytics)

---

## Indexes Strategy

### Primary Indexes
- Primary keys (automatic)
- Unique constraints (email, clickbank_id, tracking_id)

### Query Optimization Indexes
- Foreign keys (user_id, campaign_id, product_id)
- Status fields (for filtering)
- Timestamp fields (for sorting/filtering)
- Composite indexes (for complex queries)

### Full-Text Search (Future)
```sql
CREATE INDEX idx_products_search ON products
    USING gin(to_tsvector('english', title || ' ' || description));
```

---

## Migrations

All schema changes are managed through **Alembic** migrations.

**Creating a migration:**
```bash
cd backend
alembic revision --autogenerate -m "Add new column"
alembic upgrade head
```

**Migration file location:**
`backend/alembic/versions/`

---

## Performance Considerations

### Connection Pooling
- Max connections: 20
- Min connections: 5
- Connection timeout: 30s

### Query Optimization
- Use indexes for WHERE clauses
- Limit result sets
- Use SELECT only needed columns
- Cache expensive queries in Redis

### Scaling Strategy
- Read replicas for analytics queries
- Partitioning for large tables (analytics_events)
- Archive old data to S3

---

## Backup Strategy

- **Frequency:** Daily at 4 AM UTC
- **Retention:** 30 days
- **Location:** AWS S3
- **Type:** Full database dump
- **Restoration:** Automated scripts

---

This schema supports:
- **100,000+ users**
- **1M+ products**
- **10M+ analytics events**
- **Sub-50ms query performance**
