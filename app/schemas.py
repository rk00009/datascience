# app/schemas.py

from typing import Literal

from pydantic import BaseModel, Field, computed_field


# ============================================================
# SEARCH PLAN
# ============================================================

class SearchPlan(BaseModel):
    original_query: str
    product: str

    product_synonyms: list[str] = Field(default_factory=list)

    seller_origin: str | None = None
    target_market: str | None = None

    buyer_types: list[str] = Field(default_factory=list)
    buying_signals: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)

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
    queries: list[SearchQuery] = Field(default_factory=list)


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


RankedSearchQuery = RankedQuery
RankedSearchQueryList = RankedQueryList


# ============================================================
# SERP
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

    def __iter__(self):
        return iter(self.results)

    def __len__(self):
        return len(self.results)


# ============================================================
# URL / LEAD CLASSIFICATION
#
# This is the object passed from:
#
# SERP
#   ↓
# URL FILTER
#   ↓
# LEAD SELECTION
#   ↓
# CRAWLER
#
# It therefore contains ALL fields needed by main.py
# before company extraction.
# ============================================================

class URLClassification(BaseModel):

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    url: str

    website: str | None = None

    domain: str = ""

    # --------------------------------------------------------
    # SERP INFORMATION
    # --------------------------------------------------------

    title: str = ""

    snippet: str = ""

    query: str = ""

    # --------------------------------------------------------
    # COMPANY PREVIEW
    # --------------------------------------------------------

    company_name: str | None = None

    country: str | None = None

    company_type: str | None = None

    # --------------------------------------------------------
    # LEAD SCORING
    # --------------------------------------------------------

    relevance_score: float = Field(
        default=0,
        ge=0,
        le=100
    )

    lead_probability: float = Field(
        default=0,
        ge=0,
        le=100
    )

    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    is_company_candidate: bool = False

    is_lead: bool = False

    keep: bool = False

    # --------------------------------------------------------
    # REASON
    # --------------------------------------------------------

    reason: str = ""

    classification_reason: str = ""

    # --------------------------------------------------------
    # CRAWLER COMPATIBILITY
    # --------------------------------------------------------

    @computed_field
    @property
    def crawler_url(self) -> str:
        return self.website or self.url

    @computed_field
    @property
    def display_name(self) -> str:
        if self.company_name:
            return self.company_name

        if self.title:
            return self.title

        return self.domain or self.url


class URLClassificationList(BaseModel):

    results: list[URLClassification] = Field(
        default_factory=list
    )

    @computed_field
    @property
    def selected_leads(self) -> list[URLClassification]:

        return [
            item
            for item in self.results
            if item.is_lead
        ]

    @computed_field
    @property
    def accepted(self) -> list[URLClassification]:

        return [
            item
            for item in self.results
            if item.keep
        ]

    def __iter__(self):
        return iter(self.results)

    def __len__(self):
        return len(self.results)


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

    @computed_field
    @property
    def results(self) -> list[CompanyProfile]:
        return self.companies

    def __iter__(self):
        return iter(self.companies)

    def __len__(self):
        return len(self.companies)