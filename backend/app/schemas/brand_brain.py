from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from .brand import BrandResponse

class BrandVoiceBase(BaseModel):
    tone: Optional[str] = None
    personality: Optional[str] = None
    writing_style: Optional[str] = None
    preferred_language: Optional[str] = None
    formality: Optional[str] = None
    humor: Optional[str] = None
    words_to_use: Optional[str] = None
    words_to_avoid: Optional[str] = None
    messaging_rules: Optional[str] = None

class BrandVoiceUpdate(BrandVoiceBase):
    pass

class BrandVoiceResponse(BrandVoiceBase):
    id: UUID
    brand_id: UUID
    model_config = ConfigDict(from_attributes=True)


class AudienceBase(BaseModel):
    name: str
    description: Optional[str] = None
    demographics: Optional[str] = None
    pain_points: Optional[str] = None
    needs: Optional[str] = None
    goals: Optional[str] = None
    objections: Optional[str] = None
    buying_triggers: Optional[str] = None
    preferred_channels: Optional[str] = None

class AudienceCreate(AudienceBase):
    pass

class AudienceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    demographics: Optional[str] = None
    pain_points: Optional[str] = None
    needs: Optional[str] = None
    goals: Optional[str] = None
    objections: Optional[str] = None
    buying_triggers: Optional[str] = None
    preferred_channels: Optional[str] = None

class AudienceResponse(AudienceBase):
    id: UUID
    brand_id: UUID
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[str] = None
    value_proposition: Optional[str] = None
    features: Optional[str] = None
    benefits: Optional[str] = None
    target_audience: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = "active"

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[str] = None
    value_proposition: Optional[str] = None
    features: Optional[str] = None
    benefits: Optional[str] = None
    target_audience: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = None

class ProductResponse(ProductBase):
    id: UUID
    brand_id: UUID
    model_config = ConfigDict(from_attributes=True)


class PositioningBase(BaseModel):
    positioning_statement: Optional[str] = None
    unique_value_proposition: Optional[str] = None
    differentiators: Optional[str] = None
    key_messages: Optional[str] = None
    proof_points: Optional[str] = None
    market_category: Optional[str] = None

class PositioningUpdate(PositioningBase):
    pass

class PositioningResponse(PositioningBase):
    id: UUID
    brand_id: UUID
    model_config = ConfigDict(from_attributes=True)


class GoalBase(BaseModel):
    goal: str
    target_value: Optional[str] = None
    current_value: Optional[str] = None
    timeframe: Optional[str] = None
    priority: Optional[int] = 0
    status: Optional[str] = "active"

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    goal: Optional[str] = None
    target_value: Optional[str] = None
    current_value: Optional[str] = None
    timeframe: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None

class GoalResponse(GoalBase):
    id: UUID
    brand_id: UUID
    model_config = ConfigDict(from_attributes=True)


class CompetitorBase(BaseModel):
    name: str
    website: Optional[str] = None
    description: Optional[str] = None
    positioning: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "active"

class CompetitorCreate(CompetitorBase):
    pass

class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    positioning: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class CompetitorResponse(CompetitorBase):
    id: UUID
    brand_id: UUID
    model_config = ConfigDict(from_attributes=True)


class StrategyBase(BaseModel):
    business_strategy: Optional[str] = None
    marketing_strategy: Optional[str] = None
    content_strategy: Optional[str] = None
    channel_strategy: Optional[str] = None
    growth_strategy: Optional[str] = None
    campaign_strategy: Optional[str] = None

class StrategyUpdate(StrategyBase):
    pass

class StrategyResponse(StrategyBase):
    id: UUID
    brand_id: UUID
    model_config = ConfigDict(from_attributes=True)


class BrandDocumentBase(BaseModel):
    name: str
    type: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "active"
    metadata_json: Optional[Dict[str, Any]] = {}

class BrandDocumentResponse(BrandDocumentBase):
    id: UUID
    brand_id: UUID
    workspace_id: UUID
    model_config = ConfigDict(from_attributes=True)


class BrandContextResponse(BaseModel):
    brand: BrandResponse
    voice: Optional[BrandVoiceResponse] = None
    audiences: List[AudienceResponse] = []
    products: List[ProductResponse] = []
    positioning: Optional[PositioningResponse] = None
    goals: List[GoalResponse] = []
    competitors: List[CompetitorResponse] = []
    strategy: Optional[StrategyResponse] = None
    documents: List[BrandDocumentResponse] = []
    model_config = ConfigDict(from_attributes=True)
