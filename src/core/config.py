from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Car Finder"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    ALLOWED_HOSTS: str = Field(default="*", description="Allowed CORS origins (comma-separated)")
    
    # Database
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017/carfinder",
        description="MongoDB connection string"
    )
    MONGODB_DATABASE: str = Field(default="carfinder", description="MongoDB database name")
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection string"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT tokens"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24 * 8,  # 8 days
        description="Access token expiration time in minutes"
    )
    
    # External APIs
    FIRECRAWL_API_KEY: str = Field(
        default="",
        description="Firecrawl API key for web scraping"
    )
    PERPLEXITY_API_KEY: str = Field(
        default="",
        description="Perplexity API key for market research"
    )
    
    # SMTP Configuration
    SMTP_HOST: str = Field(default="localhost", description="SMTP server host")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USER: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    SMTP_TLS: bool = Field(default=True, description="Use TLS for SMTP")
    EMAIL_FROM: str = Field(
        default="noreply@carfinder.com",
        description="Default sender email address"
    )
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = Field(
        default="",
        description="Telegram bot token for notifications"
    )
    
    # Business Logic
    MAX_SEARCHES_PER_USER: int = Field(
        default=10,
        description="Maximum searches per user"
    )
    MAX_OPPORTUNITIES_PER_DAY: int = Field(
        default=100,
        description="Maximum opportunities to process per day"
    )
    DEFAULT_SEARCH_INTERVAL_HOURS: int = Field(
        default=2,
        description="Default search interval in hours"
    )
    
    # Regional Settings (Florida & Georgia focus)
    TARGET_STATES: str = Field(
        default="FL,GA",
        description="Target states for analysis (comma-separated)"
    )
    
    # Tax rates and fees by state
    STATE_TAX_RATES: dict = Field(
        default={
            "FL": {
                "sales_tax": 0.06,
                "title_fee": 77.25,
                "registration_fee": 225.0,
                "dealer_fee_cap": 998.0
            },
            "GA": {
                "sales_tax": 0.04,  # base rate, varies by county
                "title_fee": 18.0,
                "registration_fee": 20.0,
                "dealer_fee_cap": None
            }
        },
        description="State-specific tax rates and fees"
    )
    
    # Transportation costs
    TRANSPORTATION_COST_PER_MILE: float = Field(
        default=0.65,
        description="Cost per mile for vehicle transportation (IRS rate)"
    )
    BASE_TRANSPORT_FEE: float = Field(
        default=200.0,
        description="Base transportation fee for long-distance moves"
    )
    
    # API Rate Limits
    FIRECRAWL_DAILY_LIMIT: int = Field(
        default=1000,
        description="Daily limit for Firecrawl API calls"
    )
    PERPLEXITY_DAILY_LIMIT: int = Field(
        default=100,
        description="Daily limit for Perplexity API calls"
    )
    
    def get_allowed_hosts_list(self) -> List[str]:
        """Convert ALLOWED_HOSTS string to list for FastAPI"""
        if self.ALLOWED_HOSTS.strip() == "*":
            return ["*"]
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
    
    def get_target_states_list(self) -> List[str]:
        """Convert TARGET_STATES string to list"""
        return [state.strip().upper() for state in self.TARGET_STATES.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings() 