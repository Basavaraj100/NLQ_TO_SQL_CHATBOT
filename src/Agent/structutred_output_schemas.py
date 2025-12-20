from pydantic import BaseModel, Field
from typing import List


#************** Schema for Intent Validation **************#
class IntentCheck(BaseModel):
    """Structured output for intent validation."""
    is_relevant: bool = Field(description="True if question is about students")
    
    
    
    
#************** Schema for SQL Generation **************#
class SQLQuery(BaseModel):
    """Valid SQL query structure."""
    sql_query: str = Field(description="SAFE SELECT query only")
