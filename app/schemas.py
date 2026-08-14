from pydantic import BaseModel
from typing import List


class SearchPlan(BaseModel):
    original_query: str
    product: str
    country: str
    buyer_types: List[str]
    keywords: List[str]
    sources: List[str]
    intent: str
    max_results: int