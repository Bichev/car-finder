# 🔥 Firecrawl & Perplexity Integration Setup Guide

This guide walks you through setting up the **Firecrawl** and **Perplexity** integrations for automated vehicle scraping and AI-powered market analysis.

## 🎯 What's New

Your Car Finder now includes:

- **🔥 Firecrawl Integration**: Automated web scraping of vehicle listings from AutoTrader, Cars.com, and CarGurus
- **🧠 Perplexity AI**: Market analysis, pricing research, and opportunity scoring
- **🚀 Search Engine**: Complete workflow from scraping to analysis to opportunities
- **📊 New API Endpoints**: Execute searches, analyze vehicles, conduct market research

## 🔑 Getting API Keys

### Firecrawl API Key

1. **Visit**: [https://firecrawl.dev](https://firecrawl.dev)
2. **Sign up** for an account
3. **Go to Dashboard** → API Keys
4. **Copy your API key**
5. **Pricing**: Free tier includes 500 requests/month

### Perplexity API Key

1. **Visit**: [https://perplexity.ai](https://perplexity.ai)
2. **Sign up** for an account  
3. **Go to Settings** → API
4. **Generate an API key**
5. **Copy your API key**
6. **Pricing**: Free tier includes limited queries

## ⚙️ Configuration

### 1. Update Environment Variables

Add these to your `.env` file:

```bash
# External API Keys (Required for full functionality)
FIRECRAWL_API_KEY=your-firecrawl-api-key-here
PERPLEXITY_API_KEY=your-perplexity-api-key-here

# API Rate Limits (adjust based on your subscription)
FIRECRAWL_DAILY_LIMIT=1000
PERPLEXITY_DAILY_LIMIT=100
```

### 2. Restart the Application

```bash
# Stop current containers
docker-compose down

# Rebuild with new environment
docker-compose up -d

# Check logs
docker-compose logs -f app
```

## 🧪 Testing the Integration

### Quick Test

```bash
# Run the comprehensive integration test
python3 test_integrations.py
```

This will test:
- ✅ Service connectivity
- ✅ API key validation  
- ✅ Market research functionality
- ✅ Vehicle scraping capabilities
- ✅ Complete search workflow

### Manual API Testing

Test individual components:

```bash
# Check service status
curl http://localhost:8000/api/v1/search-execution/marketplace-status

# Test market research
curl -X POST "http://localhost:8000/api/v1/search-execution/market-research" \
  -H "Content-Type: application/json" \
  -d '{
    "make": "Toyota",
    "model": "Camry", 
    "year": 2018,
    "location": "FL"
  }'

# Test integration
curl -X POST "http://localhost:8000/api/v1/search-execution/test-integration"
```

## 🚀 New API Endpoints

### Search Execution

**Execute a search with Firecrawl scraping:**
```http
POST /api/v1/search-execution/execute
{
  "search_id": "your-search-id",
  "force_execution": true
}
```

**Get search results:**
```http
GET /api/v1/search-execution/search/{search_id}/results?limit=20
```

### Market Research

**Conduct AI-powered market research:**
```http
POST /api/v1/search-execution/market-research
{
  "make": "Toyota",
  "model": "Camry",
  "year": 2018,
  "location": "FL"
}
```

### Vehicle Analysis

**Analyze a specific vehicle:**
```http
POST /api/v1/search-execution/analyze-vehicle
{
  "vehicle_id": "vehicle-id-here",
  "include_market_research": true
}
```

### Service Status

**Check integration health:**
```http
GET /api/v1/search-execution/marketplace-status
```

## 📊 How It Works

### 1. Search Execution Workflow

```
Create Search → Execute Search → Firecrawl Scrapes → Perplexity Analyzes → Opportunities Created
```

1. **Create Search Configuration**: Define criteria (make, model, price, location)
2. **Execute Search**: Triggers Firecrawl to scrape marketplaces
3. **Data Processing**: Normalizes and validates vehicle data
4. **AI Analysis**: Perplexity analyzes market conditions and pricing
5. **Opportunity Scoring**: Calculates profit potential and confidence
6. **Results Storage**: Saves opportunities to database

### 2. Market Analysis Features

- **Real-time pricing research** from multiple sources
- **Regional market insights** for FL/GA markets
- **Trend analysis** and market conditions
- **Competitive pricing** analysis
- **Profit calculations** with all costs included

### 3. Supported Marketplaces

- **AutoTrader**: Primary automotive marketplace
- **Cars.com**: Major vehicle listing site  
- **CarGurus**: Popular car shopping platform
- **Future**: Facebook Marketplace, local dealers

## 💰 Cost Management

### API Usage Optimization

The system includes intelligent cost management:

- **Smart Caching**: 6-hour cache for market data
- **Rate Limiting**: Respects API limits
- **Batch Processing**: Efficient scraping patterns
- **Error Handling**: Graceful failures to avoid wasted calls

### Estimated Monthly Costs

With moderate usage (5-10 searches/day):

- **Firecrawl**: $10-25/month
- **Perplexity**: $5-15/month  
- **Total**: ~$15-40/month

## 🔧 Troubleshooting

### Common Issues

**"API key not present" errors:**
```bash
# Check your .env file has the keys
grep -E "(FIRECRAWL|PERPLEXITY)" .env

# Restart the application
docker-compose restart app
```

**"Service timeout" errors:**
```bash
# Check service logs
docker-compose logs app

# Verify connectivity
curl -f http://localhost:8000/health
```

**"No vehicles found" results:**
```bash
# This is normal for new integrations
# Vehicles are only found when scraping marketplaces
# Try different search criteria or locations
```

### Debug Mode

Enable debug logging:

```bash
# In .env file
DEBUG=true

# Restart
docker-compose restart app

# Watch detailed logs
docker-compose logs -f app
```

## 📈 Usage Examples

### 1. Basic Market Research

```python
import httpx

async def research_toyota_camry():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/search-execution/market-research",
            json={
                "make": "Toyota",
                "model": "Camry",
                "year": 2018,
                "location": "FL"
            }
        )
        data = response.json()
        print(f"Market trends: {data['market_trends']}")
        print(f"Price range: {data['average_pricing']}")
```

### 2. Execute Search and Get Results

```python
async def find_opportunities():
    async with httpx.AsyncClient() as client:
        # Execute search
        exec_response = await client.post(
            "http://localhost:8000/api/v1/search-execution/execute",
            json={
                "search_id": "your-search-id",
                "force_execution": True
            }
        )
        
        # Get results
        results_response = await client.get(
            f"http://localhost:8000/api/v1/search-execution/search/your-search-id/results"
        )
        
        opportunities = results_response.json()
        for result in opportunities['results']:
            vehicle = result['vehicle']
            opp = result['opportunity']
            print(f"{vehicle['year']} {vehicle['make']} {vehicle['model']}: ${opp['projected_profit']:,.0f} profit")
```

### 3. Analyze Specific Vehicle

```python
async def analyze_vehicle(vehicle_id):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/search-execution/analyze-vehicle",
            json={"vehicle_id": vehicle_id}
        )
        
        analysis = response.json()
        print(f"Profit potential: ${analysis['profit_potential']:,.0f}")
        print(f"Confidence: {analysis['confidence_score']:.1%}")
        print(f"Recommendation: {analysis['recommended_action']}")
```

## 🎉 What's Next

Now that your integrations are working, you can:

1. **🔍 Create Search Configurations** targeting specific opportunities
2. **⚡ Set up Automated Searches** to run every few hours
3. **📧 Configure Email Alerts** for high-profit opportunities  
4. **📱 Build Dashboard Views** to monitor results
5. **📊 Analyze Market Trends** to optimize search criteria

## 🚀 Ready to Find Profitable Cars!

Your Car Finder now has the power of AI-driven market analysis and automated vehicle discovery. Start by creating search configurations and watch as it finds profitable arbitrage opportunities!

### Quick Start Commands

```bash
# 1. Make sure API is running
docker-compose ps

# 2. Test integrations  
python3 test_integrations.py

# 3. View API docs
open http://localhost:8000/docs

# 4. Create your first search via API
# 5. Execute search and analyze results
# 6. Start finding profitable opportunities! 🚗💰
``` 