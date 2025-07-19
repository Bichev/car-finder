from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic.functional_validators import BeforeValidator
from typing import List, Optional, Dict, Any, Annotated, Union
from datetime import datetime
from enum import Enum
from bson import ObjectId


def validate_object_id(v):
    """Validate ObjectId format and return as string"""
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        if ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId format")
    if v is None:
        return None
    raise ValueError("ObjectId must be a string or ObjectId")

# Create a type alias for PyObjectId that accepts ObjectId or string
PyObjectId = Annotated[Union[str, ObjectId], BeforeValidator(validate_object_id)]


class SubscriptionTier(str, Enum):
    """Subscription tier enumeration"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class AlertChannel(str, Enum):
    """Alert channel enumeration"""
    EMAIL = "email"
    TELEGRAM = "telegram"


class AlertStatus(str, Enum):
    """Alert status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class OpportunityStatus(str, Enum):
    """Opportunity status enumeration"""
    NEW = "new"
    ALERTED = "alerted"
    VIEWED = "viewed"
    DISMISSED = "dismissed"


# Base model with common fields
class BaseDocument(BaseModel):
    """Base document model"""
    id: Optional[str] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True


# Alert Preferences
class AlertPreferences(BaseModel):
    """User alert preferences"""
    email: bool = True
    telegram: bool = False
    min_profit_threshold: float = Field(default=2000.0, description="Minimum profit to trigger alert")
    max_alerts_per_day: int = Field(default=10, description="Maximum alerts per day")


# User Model
class User(BaseDocument):
    """User document model"""
    email: EmailStr = Field(..., description="User email address")
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.STARTER)
    telegram_chat_id: Optional[str] = Field(default=None, description="Telegram chat ID for notifications")
    alert_preferences: AlertPreferences = Field(default_factory=AlertPreferences)
    is_active: bool = Field(default=True)


class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    subscription_tier: SubscriptionTier = SubscriptionTier.STARTER
    telegram_chat_id: Optional[str] = None


class UserUpdate(BaseModel):
    """User update model"""
    subscription_tier: Optional[SubscriptionTier] = None
    telegram_chat_id: Optional[str] = None
    alert_preferences: Optional[AlertPreferences] = None
    is_active: Optional[bool] = None


# Search Criteria
class SearchCriteria(BaseModel):
    """Search criteria model"""
    makes: List[str] = Field(default_factory=list, description="Vehicle makes to search for")
    models: List[str] = Field(default_factory=list, description="Vehicle models to search for")
    year_min: Optional[int] = Field(default=2010, description="Minimum year")
    year_max: Optional[int] = Field(default=2023, description="Maximum year")
    price_min: Optional[float] = Field(default=5000, description="Minimum price")
    price_max: Optional[float] = Field(default=50000, description="Maximum price")
    mileage_max: Optional[int] = Field(default=150000, description="Maximum mileage")
    locations: List[str] = Field(default_factory=list, description="Target locations/states")

    @field_validator('year_min', 'year_max')
    @classmethod
    def validate_year(cls, v):
        if v and (v < 1990 or v > 2030):
            raise ValueError('Year must be between 1990 and 2030')
        return v

    @field_validator('price_min', 'price_max')
    @classmethod
    def validate_price(cls, v):
        if v and v < 0:
            raise ValueError('Price must be positive')
        return v


# Search Model
class Search(BaseDocument):
    """Search configuration document model"""
    user_id: str = Field(..., description="User ID who owns this search")
    name: str = Field(..., description="Search configuration name")
    criteria: SearchCriteria = Field(..., description="Search criteria")
    schedule_cron: str = Field(default="0 */2 * * *", description="Cron schedule for automated searches")
    is_active: bool = Field(default=True)
    last_executed: Optional[datetime] = Field(default=None)


class SearchCreate(BaseModel):
    """Search creation model"""
    name: str
    criteria: SearchCriteria
    schedule_cron: str = "0 */2 * * *"


class SearchUpdate(BaseModel):
    """Search update model"""
    name: Optional[str] = None
    criteria: Optional[SearchCriteria] = None
    schedule_cron: Optional[str] = None
    is_active: Optional[bool] = None


# Vehicle Location
class VehicleLocation(BaseModel):
    """Vehicle location model"""
    city: str
    state: str
    coordinates: List[float] = Field(default_factory=list, description="[longitude, latitude]")


# Vehicle Model
class Vehicle(BaseDocument):
    """Vehicle document model"""
    source: str = Field(..., description="Data source (autotrader, cars.com, etc.)")
    external_id: str = Field(..., description="External listing ID")
    make: str = Field(..., description="Vehicle make")
    model: str = Field(..., description="Vehicle model")
    year: int = Field(..., description="Vehicle year")
    mileage: int = Field(..., description="Vehicle mileage")
    price: float = Field(..., description="Listed price")
    location: VehicleLocation = Field(..., description="Vehicle location")
    url: str = Field(..., description="Listing URL")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    features: List[str] = Field(default_factory=list, description="Vehicle features")
    condition: Optional[str] = Field(default=None, description="Vehicle condition")
    vin: Optional[str] = Field(default=None, description="Vehicle VIN")
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


# Market Analysis
class MarketAnalysis(BaseModel):
    """Market analysis data"""
    kbb_value: Optional[float] = Field(default=None, description="KBB estimated value")
    edmunds_value: Optional[float] = Field(default=None, description="Edmunds estimated value")
    perplexity_insights: Optional[Dict[str, Any]] = Field(default=None, description="Perplexity AI insights")
    comparable_prices: List[float] = Field(default_factory=list, description="Comparable vehicle prices")
    market_average: Optional[float] = Field(default=None, description="Market average price")


# Cost Breakdown
class CostBreakdown(BaseModel):
    """Cost breakdown model"""
    purchase_price: float = Field(..., description="Vehicle purchase price")
    sales_tax: float = Field(..., description="Sales tax amount")
    title_fee: float = Field(..., description="Title fee")
    registration_fee: float = Field(..., description="Registration fee")
    transportation_cost: float = Field(..., description="Transportation cost")
    total_cost: float = Field(..., description="Total acquisition cost")


# Opportunity Model
class Opportunity(BaseDocument):
    """Opportunity document model"""
    vehicle_id: str = Field(..., description="Associated vehicle ID")
    search_id: str = Field(..., description="Search that found this opportunity")
    market_analysis: MarketAnalysis = Field(..., description="Market analysis data")
    cost_breakdown: CostBreakdown = Field(..., description="Cost breakdown")
    projected_profit: float = Field(..., description="Projected profit amount")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    status: OpportunityStatus = Field(default=OpportunityStatus.NEW)


# Alert Model
class Alert(BaseDocument):
    """Alert document model"""
    opportunity_id: str = Field(..., description="Associated opportunity ID")
    user_id: str = Field(..., description="User to notify")
    channel: AlertChannel = Field(..., description="Notification channel")
    status: AlertStatus = Field(default=AlertStatus.PENDING)
    sent_at: Optional[datetime] = Field(default=None)
    message_id: Optional[str] = Field(default=None, description="External message ID")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


# API Response Models
class OpportunityResponse(BaseModel):
    """Opportunity response model for API"""
    id: str
    vehicle: Vehicle
    market_analysis: MarketAnalysis
    cost_breakdown: CostBreakdown
    projected_profit: float
    confidence_score: float
    status: OpportunityStatus
    created_at: datetime


class SearchResponse(BaseModel):
    """Search response model for API"""
    id: str
    name: str
    criteria: SearchCriteria
    schedule_cron: str
    is_active: bool
    last_executed: Optional[datetime]
    created_at: datetime


class UserResponse(BaseModel):
    """User response model for API"""
    id: str
    email: str
    subscription_tier: SubscriptionTier
    alert_preferences: AlertPreferences
    created_at: datetime


# Pagination
class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any]
    total: int
    skip: int
    limit: int
    has_next: bool 