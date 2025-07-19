# Car Finder - Requirements Document

## 1. Project Overview

The Car Finder is an automated system for discovering, analyzing, and evaluating used car purchase opportunities for resale arbitrage. The system will monitor multiple auto dealerships and online marketplaces to identify underpriced vehicles with resale potential.

## 2. Functional Requirements

### 2.1 Car Search & Discovery
- **FR-001**: System shall search for specific car models, makes, and years
- **FR-002**: System shall search within specified price ranges ($X to $Y)
- **FR-003**: System shall support multiple search criteria combinations (make + model + year + price range)
- **FR-004**: System shall execute searches automatically every 2 hours
- **FR-005**: System shall search multiple data sources (dealership websites, online marketplaces)
- **FR-006**: System shall handle search rate limiting and implement respectful crawling practices

### 2.2 Market Analysis & Pricing
- **FR-007**: System shall collect current market prices for found vehicles from multiple sources
- **FR-008**: System shall calculate average market price for similar vehicles (same make/model/year/mileage)
- **FR-009**: System shall identify price outliers (significantly below market value)
- **FR-010**: System shall track price history and trends over time
- **FR-011**: System shall factor in vehicle condition, mileage, and location in price analysis

### 2.3 Resale Opportunity Analysis
- **FR-012**: System shall analyze resale potential based on location (Florida and Georgia initially)
- **FR-013**: System shall calculate transportation costs between purchase and resale locations
- **FR-014**: System shall factor in state-specific taxes, fees, and registration costs
- **FR-015**: System shall estimate total acquisition costs (purchase + taxes + transportation + fees)
- **FR-016**: System shall calculate projected profit margins after all costs
- **FR-017**: System shall identify regulatory requirements for vehicle resale in target states

### 2.4 Decision Making & Alerts
- **FR-018**: System shall score opportunities based on profit potential and risk factors
- **FR-019**: System shall generate alerts for high-value opportunities (configurable thresholds)
- **FR-020**: System shall provide detailed analysis reports for each opportunity
- **FR-021**: System shall track and learn from past decisions to improve scoring algorithms
- **FR-022**: System shall support manual override and custom scoring criteria

### 2.5 Data Management
- **FR-023**: System shall store historical vehicle listings and price data
- **FR-024**: System shall maintain a database of processed opportunities and outcomes
- **FR-025**: System shall export data in common formats (CSV, JSON, PDF reports)
- **FR-026**: System shall implement data retention policies and cleanup procedures

## 3. Non-Functional Requirements

### 3.1 Performance
- **NFR-001**: Search cycles shall complete within 30 minutes per execution
- **NFR-002**: System shall handle concurrent searches across multiple sources
- **NFR-003**: Market analysis shall complete within 5 minutes per vehicle
- **NFR-004**: System shall support monitoring of at least 100 vehicles simultaneously

### 3.2 Reliability & Availability
- **NFR-005**: System shall have 95% uptime during business hours
- **NFR-006**: System shall gracefully handle failed searches and continue operation
- **NFR-007**: System shall implement retry mechanisms for transient failures
- **NFR-008**: System shall provide error logging and monitoring capabilities

### 3.3 Cost Efficiency
- **NFR-009**: Monthly operational costs shall not exceed $200 for API calls and services
- **NFR-010**: System shall implement rate limiting to avoid excessive API usage
- **NFR-011**: System shall use cost-effective data sources (free APIs where possible)
- **NFR-012**: System shall optimize search patterns to minimize redundant data collection

### 3.4 Scalability
- **NFR-013**: System shall easily expand to additional states beyond Florida and Georgia
- **NFR-014**: System shall support adding new vehicle search sources without code changes
- **NFR-015**: System shall handle increased search frequency (down to 30-minute intervals)
- **NFR-016**: System architecture shall support horizontal scaling if needed

### 3.5 Security & Compliance
- **NFR-017**: System shall respect robots.txt and terms of service of data sources
- **NFR-018**: System shall implement appropriate delays between requests to avoid being blocked
- **NFR-019**: System shall not store sensitive personal information from listings
- **NFR-020**: System shall comply with applicable data privacy regulations

## 4. Technical Requirements

### 4.1 Data Sources Integration
- **TR-001**: Integration with Perplexity AI for market research and analysis
- **TR-002**: Integration with Firecrawl for web scraping and data extraction
- **TR-003**: Support for multiple auto marketplace APIs (AutoTrader, Cars.com, etc.)
- **TR-004**: Ability to add custom dealership website scrapers
- **TR-005**: Integration with vehicle valuation services (KBB, Edmunds, NADA)

### 4.2 Technology Stack
- **TR-006**: Python-based backend for core logic and automation
- **TR-007**: Reliable database for data persistence (MongoDB for flexible document storage)
- **TR-008**: Task scheduling system for automated searches (Celery, APScheduler)
- **TR-009**: Web interface for configuration and monitoring (optional for MVP)
- **TR-010**: Logging and monitoring infrastructure

### 4.3 Deployment & Infrastructure
- **TR-011**: Containerized deployment using Docker
- **TR-012**: Cloud deployment capability (AWS, GCP, or local server)
- **TR-013**: Automated backup and disaster recovery procedures
- **TR-014**: Configuration management for different environments

## 5. Business Requirements

### 5.1 Target Markets
- **BR-001**: Initial focus on Florida and Georgia used car markets
- **BR-002**: Support for popular vehicle categories (sedans, SUVs, trucks)
- **BR-003**: Price range focus: $5,000 - $50,000 (adjustable)
- **BR-004**: Age range focus: 2010-2020 model years (adjustable)

### 5.2 Success Metrics
- **BR-005**: Identify at least 10 potential opportunities per week
- **BR-006**: Achieve 70% accuracy in profit potential predictions
- **BR-007**: Reduce manual research time by 90%
- **BR-008**: Target minimum profit margin of $2,000 per vehicle
- **BR-009**: False positive rate below 20% for high-confidence alerts

### 5.3 Constraints
- **BR-010**: Must operate within legal boundaries of web scraping and data collection
- **BR-011**: Must not disrupt normal operations of data source websites
- **BR-012**: Must maintain cost-effectiveness to ensure positive ROI
- **BR-013**: Must provide audit trail for all decisions and calculations

## 6. Assumptions and Dependencies

### 6.1 Assumptions
- **A-001**: Target data sources will remain accessible and maintain current structure
- **A-002**: Vehicle market data sources will provide reasonably accurate pricing
- **A-003**: Transportation costs can be estimated using standard mileage rates
- **A-004**: Tax and fee information for target states will be available from public sources
- **A-005**: Manual verification and final purchase decisions will be made by users

### 6.2 Dependencies
- **D-001**: Availability and reliability of Perplexity AI and Firecrawl services
- **D-002**: Continued access to vehicle marketplace websites and APIs
- **D-003**: Accurate and up-to-date tax and regulatory information
- **D-004**: Stable internet connectivity for continuous operation
- **D-005**: User expertise in vehicle evaluation and purchasing processes

## 7. Future Enhancements

### 7.1 Phase 2 Features
- **FE-001**: Mobile application for real-time alerts and analysis
- **FE-002**: Machine learning models for improved opportunity scoring
- **FE-003**: Integration with financing options and loan calculators
- **FE-004**: Automated auction bidding capabilities
- **FE-005**: Expansion to additional states and regions

### 7.2 Advanced Analytics
- **FE-006**: Seasonal trend analysis and market timing
- **FE-007**: Vehicle depreciation modeling and predictions
- **FE-008**: Competitor analysis and market positioning
- **FE-009**: ROI tracking and performance analytics
- **FE-010**: Risk assessment and mitigation strategies 