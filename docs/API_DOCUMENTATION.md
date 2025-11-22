# API Documentation

Base URL: `https://api.yourapp.com/api/v1`

## Authentication

All protected endpoints require a JWT access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Endpoints

#### POST /auth/signup
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "tier": "starter",
  "status": "trial",
  "is_email_verified": false,
  "created_at": "2025-01-01T00:00:00Z",
  "trial_ends_at": "2025-01-15T00:00:00Z"
}
```

---

#### POST /auth/login
Authenticate and receive JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

---

#### POST /auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

---

## Users

#### GET /users/me
Get current user profile. 🔒 Protected

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "tier": "professional",
  "status": "active",
  "is_email_verified": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

#### GET /users/me/usage
Get current usage statistics. 🔒 Protected

**Response:** `200 OK`
```json
{
  "content_generated": 45,
  "content_limit": 50,
  "campaigns_active": 1,
  "campaigns_limit": 1,
  "storage_used_gb": 0.5,
  "storage_limit_gb": 5
}
```

---

## Products

#### GET /products/search
Search ClickBank products. 🔒 Protected

**Query Parameters:**
- `query` (string): Search term
- `category` (string): Product category
- `min_gravity` (number): Minimum gravity score
- `max_refund_rate` (number): Maximum refund rate
- `min_commission` (number): Minimum commission amount
- `has_rebill` (boolean): Filter by recurring billing
- `limit` (number): Results per page (max 100)
- `offset` (number): Pagination offset

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "clickbank_id": "product123",
    "title": "Weight Loss Guide",
    "vendor": "VendorName",
    "category": "Health & Fitness",
    "commission_amount": 47.50,
    "gravity": 85.3,
    "refund_rate": 5.2,
    "rebill": false,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

---

## Campaigns

#### GET /campaigns
List user's campaigns. 🔒 Protected

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "product_id": "uuid",
    "name": "Weight Loss Campaign",
    "status": "active",
    "funnel_type": "review",
    "tracking_id": "ABC12345",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

---

#### POST /campaigns
Create a new campaign. 🔒 Protected

**Request:**
```json
{
  "name": "My Campaign",
  "product_id": "uuid",
  "funnel_type": "review",
  "affiliate_link": "https://hop.clickbank.net/..."
}
```

**Response:** `201 Created`

---

## Analytics

#### GET /analytics/dashboard
Get dashboard metrics. 🔒 Protected

**Response:** `200 OK`
```json
{
  "total_clicks": 1250,
  "total_conversions": 42,
  "total_revenue": 1995.00,
  "conversion_rate": 3.36,
  "average_commission": 47.50,
  "active_campaigns": 3
}
```

---

## Webhooks

#### POST /webhooks/clickbank/ipn
ClickBank Instant Payment Notification.

**Headers:**
- No authentication required (verified by signature)

**Request:** Form data from ClickBank

---

#### POST /webhooks/stripe
Stripe webhook events.

**Headers:**
- `Stripe-Signature`: Webhook signature

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "This feature requires professional tier or higher"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "detail": "An unexpected error occurred"
}
```

---

## Rate Limits

- **Starter:** 100 requests/hour
- **Professional:** 500 requests/hour
- **Agency:** 2000 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## Interactive Documentation

Visit `/docs` for Swagger UI interactive documentation.
Visit `/redoc` for ReDoc documentation.
