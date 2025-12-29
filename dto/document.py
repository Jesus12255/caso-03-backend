from typing import List, Optional, Any
from pydantic import BaseModel

class FieldRequest(BaseModel):
    label: str
    value: Any

class DocumentRequest(BaseModel):
    confidence: Optional[float] = None 
    detectedType: Optional[str] = None
    fields: List[FieldRequest]
    fileName: Optional[str] = None
    isAnonymized: bool
    isEncrypted: Optional[bool] = None

    class Config:
        orm_mode = True 