# Car Finder - Automated Used Car Arbitrage System

An intelligent automation platform that identifies profitable used car arbitrage opportunities by continuously monitoring multiple marketplaces, analyzing market conditions, and calculating resale potential across different geographic regions.

## 🚀 Features

- **Automated Market Monitoring**: 24/7 scanning of multiple car marketplaces
- **Intelligent Analysis**: AI-powered market research using Perplexity AI
- **Cost Calculation**: Comprehensive cost modeling (taxes, transportation, fees)
- **Real-time Alerts**: Email and Telegram notifications for opportunities
- **Regional Focus**: Optimized for Florida and Georgia markets
- **Web Dashboard**: React-based interface for managing searches and opportunities

## 🏗️ Architecture

- **Backend**: FastAPI with async Python
- **Database**: MongoDB for flexible document storage
- **Cache**: Redis for performance optimization
- **Task Queue**: Celery for background processing
- **Integrations**: Firecrawl MCP + Perplexity AI MCP
- **Notifications**: SMTP email + Telegram Bot API

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose
- MongoDB 7+
- Redis 7+
- API Keys for Firecrawl and Perplexity
- SMTP server access
- Telegram Bot (optional)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd car-finder
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with the following configuration:

```bash
# Application Configuration
DEBUG=true
ALLOWED_HOSTS=*
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database Configuration
MONGODB_URL=mongodb://localhost:27017/carfinder
MONGODB_DATABASE=carfinder
REDIS_URL=redis://localhost:6379

# External API Keys
FIRECRAWL_API_KEY=your-firecrawl-api-key-here
PERPLEXITY_API_KEY=your-perplexity-api-key-here

# SMTP Configuration
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USER=your-email@domain.com
SMTP_PASSWORD=your-email-password
SMTP_TLS=true
EMAIL_FROM=noreply@carfinder.com

# Telegram Bot Configuration (Optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here

# Business Configuration
MAX_SEARCHES_PER_USER=10
MAX_OPPORTUNITIES_PER_DAY=100
DEFAULT_SEARCH_INTERVAL_HOURS=2

# Regional Settings
TARGET_STATES=FL,GA
TRANSPORTATION_COST_PER_MILE=0.65
BASE_TRANSPORT_FEE=200.0

# API Rate Limits
FIRECRAWL_DAILY_LIMIT=1000
PERPLEXITY_DAILY_LIMIT=100
```

### 3. Using Docker (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### 4. Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Start MongoDB and Redis (or use Docker)
docker run -d -p 27017:27017 mongo:7
docker run -d -p 6379:6379 redis:7-alpine

# Run the application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Quick Test

Run the automated test script to verify everything is working:

```bash
python3 test_api.py
```

This will test all major API endpoints and confirm your setup is correct.

For detailed instructions, see [GETTING_STARTED.md](GETTING_STARTED.md).

## 🔧 API Endpoints

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user
- `PUT /api/v1/users/{user_id}` - Update user
- `GET /api/v1/users/email/{email}` - Get user by email

### Searches
- `POST /api/v1/searches/` - Create search configuration
- `GET /api/v1/searches/` - List searches
- `PUT /api/v1/searches/{search_id}` - Update search
- `POST /api/v1/searches/{search_id}/execute` - Execute search manually

### Opportunities
- `GET /api/v1/opportunities/` - List opportunities
- `GET /api/v1/opportunities/{opportunity_id}` - Get opportunity details
- `PUT /api/v1/opportunities/{opportunity_id}/status` - Update status
- `GET /api/v1/opportunities/top/{limit}` - Get top opportunities

### Vehicles
- `GET /api/v1/vehicles/` - List vehicles with filtering
- `GET /api/v1/vehicles/{vehicle_id}` - Get vehicle details
- `GET /api/v1/vehicles/search/similar/{vehicle_id}` - Find similar vehicles
- `GET /api/v1/vehicles/stats/summary` - Get statistics

## 🎯 Usage Examples

### 1. Create a User

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dealer@example.com",
    "subscription_tier": "professional",
    "telegram_chat_id": "123456789"
  }'
```

### 2. Create a Search Configuration

```bash
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

### 3. Get Top Opportunities

```bash
curl "http://localhost:8000/api/v1/opportunities/top/10?user_id=USER_ID"
```

## 🔐 Security Considerations

- Change the `SECRET_KEY` in production
- Use environment variables for sensitive data
- Implement proper authentication/authorization
- Rate limit API endpoints
- Monitor for suspicious activity

## 📈 Monitoring

The application includes:

- Health check endpoint (`/health`)
- Comprehensive logging with Loguru
- Database indexes for performance
- Error handling and retry mechanisms

## 🚧 Development Status

**Current Status**: ✅ Core Backend Complete

**Next Steps**:
1. Implement Firecrawl and Perplexity integrations
2. Build search execution engine
3. Create analysis and scoring algorithms
4. Implement notification system
5. Build React frontend
6. Add comprehensive testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Support

For questions or support, please contact the development team.

---

**Built with ❤️ for car dealers and flippers looking to automate their arbitrage strategies.** 