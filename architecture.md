# Car Finder - Technical Architecture Document

## 1. System Overview

### 1.1 Architecture Vision
The Car Finder system follows a cloud-native, microservices-based architecture designed for scalability, reliability, and cost-effectiveness. The system emphasizes automated data collection, intelligent analysis, and real-time notifications while maintaining operational efficiency.

### 1.2 Design Principles
- **Modularity**: Loosely coupled services for independent scaling and maintenance
- **Automation**: Minimize manual intervention in data collection and analysis
- **Cost Optimization**: Intelligent resource usage to stay within budget constraints
- **Scalability**: Horizontal scaling capabilities for growing user base
- **Reliability**: Fault tolerance and graceful degradation
- **Data Privacy**: Minimal storage of sensitive information, GDPR compliance

### 1.3 High-Level Architecture

```
┌─────────────────┐                             ┌─────────────────┐
│   Web Client    │                             │   API Client    │
│   (React)       │                             │  (Enterprise)   │
└─────────────────┘                             └─────────────────┘
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   API Gateway   │
                    │   (FastAPI)     │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Search Service │    │Analysis Service │    │ Alert Service   │
│   (Python)      │    │   (Python)      │    │   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Data Layer    │
                    │  (MongoDB +     │
                    │     Redis)      │
                    └─────────────────┘
```

## 2. System Components

### 2.1 Core Services

#### 2.1.1 API Gateway Service
**Technology**: FastAPI with Pydantic validation  
**Responsibilities**:
- Request routing and load balancing
- Authentication and authorization
- Rate limiting and throttling
- Request/response logging and monitoring
- API versioning and documentation

**Key Endpoints**:
```
GET    /api/v1/searches          - List user searches
POST   /api/v1/searches          - Create new search
GET    /api/v1/opportunities     - List opportunities
GET    /api/v1/analytics         - Get analytics data
POST   /api/v1/alerts/config     - Configure alerts
```

#### 2.1.2 Search Service
**Technology**: Python with asyncio for concurrent processing  
**Responsibilities**:
- Managing search configurations and schedules
- Coordinating data collection from multiple sources
- Deduplicating and normalizing vehicle data
- Triggering analysis workflows

**Key Components**:
- **Search Scheduler**: APScheduler for automated search execution
- **Data Collectors**: Modular collectors for different sources
- **Data Normalizer**: Standardize vehicle data across sources
- **Search Manager**: Orchestrate search workflows

#### 2.1.3 Analysis Service
**Technology**: Python with pandas and scikit-learn  
**Responsibilities**:
- Market price analysis and comparison
- Profit calculation with cost modeling
- Opportunity scoring and ranking
- Historical trend analysis

**Analysis Modules**:
- **Price Analyzer**: Compare prices across markets and historical data
- **Cost Calculator**: Comprehensive cost modeling (taxes, transportation, fees)
- **Profit Estimator**: Revenue projections with confidence intervals
- **Risk Assessor**: Market volatility and vehicle-specific risks

#### 2.1.4 Alert Service
**Technology**: Python with Celery for async notifications  
**Responsibilities**:
- Managing user alert preferences
- Generating notifications based on opportunity scores
- Multi-channel notification delivery
- Alert history and analytics

**Notification Channels**:
- **Email**: SMTP server integration with template system
- **Telegram**: Bot API integration for instant messaging
- **Webhook**: Custom integrations for enterprise users

### 2.2 Data Collection Layer

#### 2.2.1 Firecrawl Integration
**Purpose**: Primary web scraping engine for vehicle marketplaces  
**Implementation**:
```python
class FirecrawlCollector:
    def __init__(self, api_key: str):
        self.client = FirecrawlClient(api_key)
    
    async def scrape_marketplace(self, search_params: SearchParams) -> List[Vehicle]:
        # Implement marketplace-specific scraping logic
        pass
    
    async def batch_scrape(self, urls: List[str]) -> List[VehicleData]:
        # Efficient batch processing of vehicle listings
        pass
```

**Targeted Sources**:
- AutoTrader.com
- Cars.com
- CarGurus.com
- Local dealership websites
- Facebook Marketplace (if accessible)

#### 2.2.2 Perplexity AI Integration
**Purpose**: Market research and pricing intelligence  
**Implementation**:
```python
class PerplexityAnalyzer:
    def __init__(self, api_key: str):
        self.client = PerplexityClient(api_key)
    
    async def get_market_analysis(self, vehicle: Vehicle) -> MarketAnalysis:
        query = f"Current market value for {vehicle.year} {vehicle.make} {vehicle.model}"
        return await self.client.research(query)
    
    async def get_regional_insights(self, location: str) -> RegionalData:
        # Get location-specific market conditions
        pass
```

#### 2.2.3 Vehicle Valuation APIs
**KBB/Edmunds Integration**:
```python
class ValuationService:
    def __init__(self):
        self.kbb_client = KBBClient(api_key)
        self.edmunds_client = EdmundsClient(api_key)
    
    async def get_valuations(self, vehicle: Vehicle) -> VehicleValuation:
        kbb_value = await self.kbb_client.get_value(vehicle)
        edmunds_value = await self.edmunds_client.get_value(vehicle)
        return self.aggregate_valuations([kbb_value, edmunds_value])
```

### 2.3 Data Storage Layer

#### 2.3.1 Primary Database (MongoDB)
**Document Structure Design**:
```javascript
// Users Collection
{
  _id: ObjectId,
  email: String, // unique index
  subscription_tier: String,
  telegram_chat_id: String, // optional for telegram notifications
  alert_preferences: {
    email: Boolean,
    telegram: Boolean,
    min_profit_threshold: Number,
    max_alerts_per_day: Number
  },
  created_at: Date,
  updated_at: Date
}

// Searches Collection
{
  _id: ObjectId,
  user_id: ObjectId, // reference to users
  name: String,
  criteria: {
    makes: [String],
    models: [String],
    year_min: Number,
    year_max: Number,
    price_min: Number,
    price_max: Number,
    mileage_max: Number,
    locations: [String]
  },
  schedule_cron: String,
  is_active: Boolean,
  created_at: Date,
  last_executed: Date
}

// Vehicles Collection
{
  _id: ObjectId,
  source: String,
  external_id: String,
  make: String,
  model: String,
  year: Number,
  mileage: Number,
  price: Number,
  location: {
    city: String,
    state: String,
    coordinates: [Number] // [longitude, latitude]
  },
  url: String,
  images: [String],
  features: [String],
  condition: String,
  vin: String, // optional
  discovered_at: Date,
  last_seen_at: Date,
  is_active: Boolean
}

// Opportunities Collection
{
  _id: ObjectId,
  vehicle_id: ObjectId, // reference to vehicles
  search_id: ObjectId, // reference to searches
  market_analysis: {
    kbb_value: Number,
    edmunds_value: Number,
    perplexity_insights: Object,
    comparable_prices: [Number],
    market_average: Number
  },
  cost_breakdown: {
    purchase_price: Number,
    sales_tax: Number,
    title_fee: Number,
    registration_fee: Number,
    transportation_cost: Number,
    total_cost: Number
  },
  projected_profit: Number,
  confidence_score: Number, // 0-1
  created_at: Date,
  status: String // "new", "alerted", "viewed", "dismissed"
}

// Alerts Collection
{
  _id: ObjectId,
  opportunity_id: ObjectId,
  user_id: ObjectId,
  channel: String, // "email" or "telegram"
  status: String, // "sent", "failed", "pending"
  sent_at: Date,
  message_id: String, // telegram message id or email id
  error_message: String // if failed
}
```

#### 2.3.2 Cache Layer (Redis)
**Usage Patterns**:
```python
# Market data caching
market_data_key = f"market:{make}:{model}:{year}"
cache.setex(market_data_key, 3600, market_data)  # 1-hour TTL

# Search result caching
search_key = f"search:{search_id}:{datetime.now().hour}"
cache.setex(search_key, 1800, search_results)  # 30-minute TTL

# User session management
session_key = f"session:{user_id}"
cache.setex(session_key, 86400, session_data)  # 24-hour TTL
```

## 3. Data Flow Architecture

### 3.1 Search Execution Flow
```
┌─────────────────┐
│   Scheduler     │
│   (APScheduler) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Search Queue   │
│   (Celery)      │
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│  Data Collector │───▶│   Firecrawl     │
│    (Async)      │    │     API         │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Data Normalizer │
│  & Validator    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│   (Vehicles)    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Analysis Queue  │
│   (Celery)      │
└─────────────────┘
```

### 3.2 Analysis Pipeline
```
┌─────────────────┐
│ New Vehicle     │
│ Detection       │
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│ Market Analysis │───▶│   Perplexity    │
│    Service      │    │      API        │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│ Valuation       │───▶│   KBB/Edmunds   │
│   Service       │    │      APIs       │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Cost Calculator │
│  & Profit Est.  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Opportunity     │
│   Scoring       │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Alert Engine    │
│ (If threshold   │
│   exceeded)     │
└─────────────────┘
```

### 3.3 Real-time Notification Flow
```
┌─────────────────┐
│ High-Score      │
│ Opportunity     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Alert Trigger   │
│   (Redis Pub/   │
│     Sub)        │
└─────────────────┘
         │
         ├─────────────────┬─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Email Service   │ │  SMS Service    │ │ Push Service    │
│    (SMTP)       │ │   (Twilio)      │ │  (Firebase)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 4. External Integrations

### 4.1 Cost-Effective API Strategy

#### 4.1.1 API Cost Management
```python
class APIRateLimiter:
    def __init__(self):
        self.daily_limits = {
            'firecrawl': 1000,    # requests per day
            'perplexity': 100,    # queries per day
            'kbb': 500,           # lookups per day
        }
        self.current_usage = {}
    
    async def can_make_request(self, service: str) -> bool:
        today_usage = await self.get_today_usage(service)
        return today_usage < self.daily_limits[service]
```

#### 4.1.2 Intelligent Caching Strategy
```python
class SmartCache:
    def __init__(self):
        self.cache_durations = {
            'market_data': 3600,      # 1 hour
            'vehicle_valuation': 86400, # 24 hours
            'regional_data': 604800,   # 1 week
        }
    
    async def get_or_fetch(self, key: str, fetch_func: callable, cache_type: str):
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        data = await fetch_func()
        ttl = self.cache_durations[cache_type]
        await self.redis.setex(key, ttl, json.dumps(data))
        return data
```

### 4.2 Regional Data Integration

#### 4.2.1 Tax and Fee Calculation
```python
class RegionalCostCalculator:
    def __init__(self):
        self.state_configs = {
            'FL': {
                'sales_tax': 0.06,
                'title_fee': 77.25,
                'registration_fee': 225,
                'dealer_fee_cap': 998,
            },
            'GA': {
                'sales_tax': 0.04,  # base rate, varies by county
                'title_fee': 18,
                'registration_fee': 20,
                'dealer_fee_cap': None,
            }
        }
    
    def calculate_total_costs(self, vehicle_price: float, state: str) -> CostBreakdown:
        config = self.state_configs[state]
        sales_tax = vehicle_price * config['sales_tax']
        total_fees = config['title_fee'] + config['registration_fee']
        return CostBreakdown(
            purchase_price=vehicle_price,
            sales_tax=sales_tax,
            fees=total_fees,
            total=vehicle_price + sales_tax + total_fees
        )
```

#### 4.2.2 Transportation Cost Estimation
```python
class TransportationCalculator:
    def __init__(self):
        self.cost_per_mile = 0.65  # IRS standard rate
        self.base_transport_fee = 200
    
    async def calculate_transport_cost(self, origin: str, destination: str) -> float:
        distance = await self.get_distance(origin, destination)
        if distance <= 50:
            return 0  # Local pickup
        elif distance <= 300:
            return self.base_transport_fee + (distance * 0.5)
        else:
            return self.base_transport_fee + (distance * self.cost_per_mile)
```

## 5. Security & Privacy

### 5.1 Authentication & Authorization
```python
class AuthService:
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET')
        self.token_expiry = 86400  # 24 hours
    
    def generate_token(self, user_id: str) -> str:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
```

### 5.2 Data Privacy Compliance
- **Data Minimization**: Only store necessary vehicle data, avoid personal seller information
- **Anonymization**: Hash or remove personally identifiable information
- **Retention Policies**: Automatic cleanup of old data based on configured retention periods
- **Access Controls**: Role-based access with audit logging

## 6. Monitoring & Observability

### 6.1 Application Monitoring
```python
import logging
from prometheus_client import Counter, Histogram, Gauge

# Metrics collection
search_requests = Counter('search_requests_total', 'Total search requests')
api_response_time = Histogram('api_response_seconds', 'API response time')
active_opportunities = Gauge('active_opportunities', 'Current active opportunities')

class MonitoringService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_search_execution(self, search_id: str, duration: float, results_count: int):
        self.logger.info(f"Search {search_id} completed in {duration}s with {results_count} results")
        search_requests.inc()
        api_response_time.observe(duration)
```

### 6.2 Error Handling & Alerts
```python
class ErrorHandler:
    def __init__(self):
        self.error_thresholds = {
            'api_failures': 10,      # per hour
            'search_failures': 5,    # per hour
            'alert_failures': 3,     # per hour
        }
    
    async def handle_api_error(self, service: str, error: Exception):
        await self.log_error(service, error)
        error_count = await self.get_error_count(service, hours=1)
        
        if error_count >= self.error_thresholds.get(f'{service}_failures', 5):
            await self.send_critical_alert(service, error_count)
```

## 7. Deployment Architecture

### 7.1 Container Strategy
```dockerfile
# Dockerfile for main application
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Docker Compose Development Setup
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017/carfinder
      - REDIS_URL=redis://redis:6379
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:7
    environment:
      MONGO_INITDB_DATABASE: carfinder
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  worker:
    build: .
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - redis
      - mongodb

volumes:
  mongodb_data:
  redis_data:
```

### 7.3 Production Deployment (AWS)
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    image: carfinder:latest
    environment:
      - MONGODB_URL=${MONGODB_ATLAS_URL}
      - REDIS_URL=${ELASTICACHE_URL}
      - FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}
      - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

## 8. Scalability Considerations

### 8.1 Horizontal Scaling Strategy
- **API Layer**: Multiple FastAPI instances behind load balancer
- **Worker Processes**: Celery workers can be scaled independently
- **Database**: MongoDB replica sets for high availability and read scaling
- **Cache**: Redis cluster for high availability

### 8.2 Performance Optimization
```python
class PerformanceOptimizer:
    def __init__(self):
        self.connection_pool_size = 20
        self.request_timeout = 30
        self.batch_size = 100
    
    async def batch_process_vehicles(self, vehicles: List[Vehicle]):
        # Process vehicles in batches to avoid memory issues
        for batch in self.chunk_list(vehicles, self.batch_size):
            await self.process_vehicle_batch(batch)
    
    def chunk_list(self, lst: List, chunk_size: int):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]
```

### 8.3 Cost Optimization
- **Scheduled Scaling**: Scale down during low-usage periods
- **Spot Instances**: Use spot instances for batch processing workers
- **Intelligent Caching**: Reduce API calls through smart caching strategies
- **Data Lifecycle**: Automatic archival of old data to reduce storage costs

## 9. Implementation Phases

### 9.1 Phase 1: Core MVP (Months 1-2)
**Components to Build**:
- Basic API Gateway with authentication
- Single marketplace integration (AutoTrader)
- Simple search and analysis pipeline
- Email notification system
- MongoDB database with document schemas

**Success Criteria**:
- Successfully scrape and analyze 100+ vehicles daily
- Generate profitable opportunity alerts
- Handle 10 concurrent users

### 9.2 Phase 2: Enhanced Features (Months 3-4)
**Components to Add**:
- Multiple marketplace integrations
- Perplexity AI integration for market analysis
- Advanced cost calculation with regional data
- Mobile app with push notifications
- Redis caching layer

**Success Criteria**:
- 90%+ uptime with multiple data sources
- Sub-5-minute analysis completion
- Support 100+ concurrent users

### 9.3 Phase 3: Production Scale (Months 5-6)
**Components to Add**:
- Full monitoring and alerting suite
- Advanced analytics and reporting
- Enterprise API features
- Automated deployment pipeline
- Performance optimization

**Success Criteria**:
- Support 1000+ users
- 99.5% uptime
- Complete cost optimization under $200/month operational costs

## 10. Risk Mitigation

### 10.1 Technical Risks
- **API Rate Limiting**: Implement intelligent request distribution and caching
- **Data Source Changes**: Modular scraper design for easy updates
- **Performance Bottlenecks**: Comprehensive monitoring and auto-scaling

### 10.2 Operational Risks
- **Cost Overruns**: Real-time cost monitoring with automatic throttling
- **Legal Compliance**: Respect robots.txt and implement respectful scraping practices
- **Data Quality**: Multiple validation layers and data quality scoring

This architecture provides a solid foundation for building a scalable, cost-effective, and reliable car finder system that can grow with user demand while maintaining operational efficiency. 