from typing import Any, ClassVar
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy import Column, DateTime, MetaData
from sqlalchemy.sql import func

@as_declarative()
class Base:
    metadata: ClassVar[MetaData]
    id: Any
    __name__: ClassVar[str]
    
    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
        
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
