# Technical Specification

## System Architecture

### Backend Components
1. **API Layer** (Flask)
   - Authentication & Authorization
   - Bot Management API
   - Advertisement API
   - Analytics API

2. **Database Layer** (PostgreSQL)
   - Users
   - Bots
   - Messages
   - Advertisements
   - Analytics
   - Logs

3. **Bot Management Service**
   - Bot Instance Manager
   - Message Broadcasting System
   - State Management

4. **Analytics Engine**
   - Usage Metrics Collection
   - Performance Monitoring
   - Advertisement Analytics

### Frontend Components
1. **Dashboard UI** (React)
   - Bot Management Interface
   - Analytics Dashboard
   - Advertisement Management
   - User Management

2. **Monitoring UI**
   - System Status
   - Error Logs
   - Performance Metrics

## Database Schema

```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    public_id VARCHAR(50) UNIQUE,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(80),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20)
);

-- Bots Table
CREATE TABLE bots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    bot_token VARCHAR(100) UNIQUE,
    bot_name VARCHAR(100),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    instance_id VARCHAR(50)
);

-- Messages Table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER REFERENCES bots(id),
    chat_id BIGINT,
    message_type VARCHAR(20),
    content TEXT,
    sent_at TIMESTAMP,
    status VARCHAR(20)
);

-- Advertisements Table
CREATE TABLE advertisements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content TEXT,
    media_urls JSON,
    price DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scheduled_for TIMESTAMP,
    completed_at TIMESTAMP
);

-- Analytics Table
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER REFERENCES bots(id),
    metric_type VARCHAR(50),
    metric_value JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logs Table
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER REFERENCES bots(id),
    log_level VARCHAR(20),
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Authentication
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/change-password

### Bot Management
- POST /api/bots/add
- POST /api/bots/{id}/start
- POST /api/bots/{id}/stop
- POST /api/bots/{id}/restart
- GET /api/bots/{id}/status
- GET /api/bots/{id}/metrics
- GET /api/bots/{id}/logs

### Advertisement
- POST /api/ads/create
- GET /api/ads/list
- POST /api/ads/{id}/broadcast
- GET /api/ads/{id}/statistics

### Analytics
- GET /api/analytics/dashboard
- GET /api/analytics/bots/{id}
- GET /api/analytics/ads
- GET /api/analytics/export

## Security Considerations
1. JWT-based authentication
2. Role-based access control
3. API rate limiting
4. Secure bot token storage
5. Audit logging

## Monitoring & Observability
1. Prometheus metrics
2. Grafana dashboards
3. ELK stack for logging
4. Error tracking with Sentry

## Deployment Architecture
1. Docker containers
2. Nginx reverse proxy
3. Redis for caching
4. PostgreSQL database
5. Supervisor for bot process management