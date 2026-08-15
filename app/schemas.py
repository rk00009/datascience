from pydantic import BaseModel
from typing import Literal


# =====================================
# SEARCH PLANNER
# =====================================

BuyerType = Literal[
    "importer",
    "distributor",
    "wholesaler",
    "food_processor",
    "manufacturer",
    "trading_company",
    "retailer"
]


class SearchPlan(BaseModel):

    original_query: str

    product: str

    product_synonyms: list[str]

    seller_origin: str | None

    target_market: str | None

    buyer_types: list[BuyerType]

    buying_signals: list[str]

    keywords: list[str]

    languages: list[str]

    intent: Literal[
        "buyer_discovery",
        "importer_discovery",
        "active_buyer_search",
        "supplier_search"
    ]

    max_results: int

    max_queries: int



# =====================================
# QUERY GENERATOR
# =====================================


QueryCategory = Literal[
    "importer",
    "distributor",
    "wholesaler",
    "food_processor",
    "manufacturer",
    "trading_company"
]


SourceType = Literal[
    "google_search",
    "trade_directory",
    "company_website",
    "trade_exhibitor",
    "public_database"
]


class SearchQuery(BaseModel):

    query: str

    category: QueryCategory

    purpose: str

    buyer_type: BuyerType

    source_type: SourceType

    language: str

    priority: Literal[
        "high",
        "medium",
        "low"
    ]



class SearchQueryList(BaseModel):

    queries: list[SearchQuery]



# =====================================
# QUERY RANKER
# =====================================


class RankedQuery(BaseModel):

    query: str

    relevance_score: float

    reason: str

    keep: bool



class RankedQueryList(BaseModel):

    selected_queries: list[RankedQuery]



# =====================================
# SERP RESULTS
# =====================================


class SERPResult(BaseModel):

    title: str | None

    url: str

    snippet: str | None



class SERPResultList(BaseModel):

    results: list[SERPResult]



# =====================================
# URL CLASSIFICATION AGENT
# =====================================


URLSourceType = Literal[
    "company_website",
    "business_directory",
    "trade_platform",
    "trade_exhibitor",
    "market_report",
    "news",
    "government",
    "social_media",
    "irrelevant"
]


class URLClassification(BaseModel):

    url: str

    title: str | None

    source_type: URLSourceType

    company_name: str | None

    is_lead: bool

    lead_probability: float

    reason: str



class URLClassificationList(BaseModel):

    results: list[URLClassification]



# =====================================
# COMPANY EXTRACTION (NEXT MODULE)
# =====================================


class CompanyProfile(BaseModel):

    company_name: str | None

    website: str

    country: str | None

    products: list[str]

    buyer_type: list[BuyerType]

    description: str | None

    email: list[str]

    phone: list[str]

    linkedin: str | None

    source_url: str

    buying_signals: list[str]



class CompanyProfileList(BaseModel):

    companies: list[CompanyProfile]



# =====================================
# FINAL LEAD SCORE
# =====================================


class LeadScore(BaseModel):

    company_name: str

    relevance_score: float

    contact_score: float

    buying_intent_score: float

    final_score: float

    explanation: str


class ScrapedWebsite(BaseModel):

    url: str

    title: str | None

    text_content: str

    pages_scraped: list[str]