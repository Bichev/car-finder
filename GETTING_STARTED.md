# 🚀 Getting Started with Car Finder

This guide will help you set up and test the Car Finder application on your local machine.

## 📋 Prerequisites

- **Python 3.10+** (we tested with Python 3.9+)
- **Docker & Docker Compose** (recommended)
- **Git** (for version control)

## 🛠️ Quick Setup (Docker - Recommended)

### 1. Create Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy this content to your .env file
# Application Configuration
DEBUG=true
SECRET_KEY=your-super-secret-key-please-change-this
ALLOWED_HOSTS=*

# Database Configuration  
MONGODB_URL=mongodb://mongodb:27017/carfinder
MONGODB_DATABASE=carfinder
REDIS_URL=redis://redis:6379

# External API Keys (Optional for now - we'll add these later)
FIRECRAWL_API_KEY=not-needed-yet
PERPLEXITY_API_KEY=not-needed-yet

# SMTP Configuration (Optional for now)
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_TLS=true
EMAIL_FROM=noreply@carfinder.com

# Telegram Bot (Optional for now)
TELEGRAM_BOT_TOKEN=

# Business Configuration
MAX_SEARCHES_PER_USER=10
MAX_OPPORTUNITIES_PER_DAY=100
DEFAULT_SEARCH_INTERVAL_HOURS=2

# Regional Settings (Florida & Georgia focus)
TARGET_STATES=FL,GA
TRANSPORTATION_COST_PER_MILE=0.65
BASE_TRANSPORT_FEE=200.0

# API Rate Limits
FIRECRAWL_DAILY_LIMIT=1000
PERPLEXITY_DAILY_LIMIT=100
```

### 2. Install Docker (macOS)

If you don't have Docker installed:

1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Docker and Docker Compose:
   ```bash
   brew install docker docker-compose
   ```

3. Install Colima (Docker runtime for macOS):
   ```bash
   brew install colima
   ```

4. Start Colima:
   ```bash
   colima start
   ```

### 3. Start the Application

```bash
# Build and start all services
docker-compose up -d

# Check if everything is running
docker-compose ps

# Watch the logs
docker-compose logs -f app
```

### 3. Verify Installation

Open your browser and go to:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Alternative Docs**: http://localhost:8000/redoc

You should see the FastAPI interactive documentation!

## 🧪 Testing the API

### Option A: Using the Interactive Docs (Easiest)

1. Go to http://localhost:8000/docs
2. You'll see all available endpoints
3. Click on any endpoint to expand it
4. Click "Try it out" to test

### Option B: Using curl Commands

#### 1. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

#### 2. Create a User
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dealer@example.com",
    "subscription_tier": "professional"
  }'
```

You'll get a response with the user ID - **save this ID** for the next steps!

#### 3. Create a Search Configuration
```bash
# Replace USER_ID with the ID from step 2
curl -X POST "http://localhost:8000/api/v1/searches/?user_id=USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Florida Toyota Camrys",
    "criteria": {
      "makes": ["Toyota"],
      "models": ["Camry"],
      "year_min": 2015,
      "year_max": 2020,
      "price_min": 15000,
      "price_max": 25000,
      "locations": ["FL"]
    },
    "schedule_cron": "0 */2 * * *"
  }'
```

#### 4. List Your Searches
```bash
# Replace USER_ID with your user ID
curl "http://localhost:8000/api/v1/searches/?user_id=USER_ID"
```

#### 5. Test Vehicle Statistics
```bash
curl "http://localhost:8000/api/v1/vehicles/stats/summary"
# This will show empty stats since we haven't added vehicles yet
```

### Option C: Using Postman or Insomnia

Import the API documentation from: `http://localhost:8000/openapi.json`

### Option D: Automated Test Script

For a comprehensive test of all endpoints:

```bash
# Install requests module (required for testing)
python3 -m pip install requests

# Run the automated test script
python3 test_api.py
```

This will test all major endpoints and show you exactly what's working!

## 📊 What You Can Test Right Now

### ✅ **Working Features:**

1. **User Management**
   - Create users with different subscription tiers
   - Update user preferences
   - Get user information

2. **Search Configuration**
   - Create search criteria (makes, models, price ranges, locations)
   - Update and manage searches
   - Subscription-based limits (Starter: 5, Professional: 25, Enterprise: 100)

3. **Data Models**
   - All MongoDB schemas are working
   - Validation for prices, years, locations
   - Proper error handling

4. **Regional Business Logic**
   - Florida and Georgia tax calculations
   - Transportation cost estimation
   - State-specific fees

### 🚧 **Not Yet Implemented (Coming Next):**

- Vehicle data collection (Firecrawl integration)
- Market analysis (Perplexity integration)  
- Opportunity scoring and alerts
- Email/Telegram notifications
- React frontend

## 🐛 Troubleshooting

### If Docker containers won't start:

```bash
# Check if ports are available
lsof -i :8000
lsof -i :27017
lsof -i :6379

# Stop any conflicting services
docker-compose down
docker system prune -f

# Restart
docker-compose up -d
```

### If you see database connection errors:

```bash
# Check MongoDB container
docker-compose logs mongodb

# Check Redis container  
docker-compose logs redis

# Restart just the database services
docker-compose restart mongodb redis
```

### If the app container fails:

```bash
# Check application logs
docker-compose logs app

# Common issues:
# 1. Missing .env file
# 2. Invalid environment variables
# 3. Port conflicts
```

## 🔧 Manual Setup (Without Docker)

If you prefer to run without Docker:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start MongoDB and Redis
```bash
# MongoDB
brew install mongodb-community  # macOS
# or
sudo apt-get install mongodb     # Ubuntu

# Redis
brew install redis              # macOS
# or  
sudo apt-get install redis-server # Ubuntu

# Start services
brew services start mongodb-community
brew services start redis
```

### 3. Update Environment
```bash
# In your .env file, change:
MONGODB_URL=mongodb://localhost:27017/carfinder
REDIS_URL=redis://localhost:6379
```

### 4. Run the Application
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📈 Next Steps

Once you have the basic system running:

1. **Test the APIs** using the examples above
2. **Explore the documentation** at http://localhost:8000/docs
3. **Create test data** (users, searches) to familiarize yourself
4. **Ready for the next phase**: We'll add Firecrawl and Perplexity integrations!

## 🆘 Need Help?

If you encounter any issues:
1. Check the logs: `docker-compose logs -f`
2. Verify your `.env` file matches the template above
3. Make sure all ports (8000, 27017, 6379) are available
4. Try restarting: `docker-compose down && docker-compose up -d`

---

**🎉 Success Criteria**: If you can access http://localhost:8000/docs and create/list users and searches, you're ready to move forward! 