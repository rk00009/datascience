# app/schemas.py

from typing import Literal

from pydantic import BaseModel, Field


# ============================================================
# SEARCH PLAN
# ============================================================

class SearchPlan(BaseModel):

    original_query: str

    product: str

    product_synonyms: list[str] = Field(
        default_factory=list
    )

    seller_origin: str | None = None

    target_market: str | None = None

    buyer_types: list[str] = Field(
        default_factory=list
    )

    buying_signals: list[str] = Field(
        default_factory=list
    )

    keywords: list[str] = Field(
        default_factory=list
    )

    languages: list[str] = Field(
        default_factory=list
    )

    intent: str = "buyer_discovery"

    max_results: int = 50

    max_queries: int = 10


# ============================================================
# SEARCH QUERY
# ============================================================

class SearchQuery(BaseModel):

    query: str

    purpose: str = ""

    buyer_type: str = ""

    priority: Literal[
        "high",
        "medium",
        "low"
    ] = "medium"


class SearchQueryList(BaseModel):

    queries: list[SearchQuery] = Field(
        default_factory=list
    )


# ============================================================
# RANKED QUERY
# ============================================================

class RankedQuery(BaseModel):

    query: str

    relevance_score: float = 0

    reason: str = ""

    keep: bool = True


class RankedQueryList(BaseModel):

    selected_queries: list[RankedQuery] = Field(
        default_factory=list
    )


# Backward compatibility
RankedSearchQuery = RankedQuery
RankedSearchQueryList = RankedQueryList


# ============================================================
# SERP RESULT
# ============================================================

class SERPResult(BaseModel):

    title: str = ""

    url: str

    snippet: str = ""

    query: str = ""

    position: int | None = None


class SERPResultList(BaseModel):

    results: list[SERPResult] = Field(
        default_factory=list
    )


# ============================================================
# URL CLASSIFICATION
# ============================================================

class URLClassification(BaseModel):

    url: str

    domain: str = ""

    # Company candidate
    is_company_candidate: bool = False

    # Lead candidate
    is_lead: bool = False

    # Company classification
    company_type: str | None = None

    # Scoring
    relevance_score: float = Field(
        default=0,
        ge=0,
        le=100
    )

    # Explanation
    reason: str = ""

    # Final URL filter decision
    keep: bool = False


class URLClassificationList(BaseModel):

    results: list[URLClassification] = Field(
        default_factory=list
    )


# ============================================================
# COMPANY PROFILE
# ============================================================

class CompanyProfile(BaseModel):

    company_name: str | None = None

    website: str | None = None

    country: str | None = None

    description: str | None = None

    buyer_type: list[str] = Field(
        default_factory=list
    )

    products: list[str] = Field(
        default_factory=list
    )

    importing_activity: bool = False

    buying_signals: list[str] = Field(
        default_factory=list
    )

    email: list[str] = Field(
        default_factory=list
    )

    phone: list[str] = Field(
        default_factory=list
    )

    address: str | None = None

    contact_page: str | None = None

    linkedin: str | None = None


class CompanyProfileList(BaseModel):

    companies: list[CompanyProfile] = Field(
        default_factory=list
    )