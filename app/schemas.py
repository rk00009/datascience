from pydantic import BaseModel
from typing import Literal


# =====================================================
# 1. SEARCH PLANNER SCHEMA
# =====================================================

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



# =====================================================
# 2. QUERY GENERATION SCHEMA
# =====================================================


QueryCategory = Literal[
    "importer",
    "distributor",
    "wholesaler",
    "food_processor",
    "manufacturer",
    "trading_company"
]


SearchSource = Literal[
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

    source_type: SearchSource

    language: str

    priority: Literal[
        "high",
        "medium",
        "low"
    ]



class SearchQueryList(BaseModel):

    queries: list[SearchQuery]



# =====================================================
# 3. QUERY RANKING SCHEMA
# =====================================================


class RankedQuery(BaseModel):

    query: str

    relevance_score: float

    reason: str

    keep: bool



class RankedQueryList(BaseModel):

    selected_queries: list[RankedQuery]



# =====================================================
# 4. SERP RESULTS SCHEMA
# =====================================================


class SERPResult(BaseModel):

    title: str | None

    url: str

    snippet: str | None



class SERPResultList(BaseModel):

    results: list[SERPResult]



# =====================================================
# 5. URL CLASSIFICATION SCHEMA
# =====================================================


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



# =====================================================
# 6. WEBSITE SCRAPER OUTPUT
# =====================================================


class ScrapedWebsite(BaseModel):

    url: str

    title: str | None

    text_content: str

    links: list[str]



class ScrapedWebsiteList(BaseModel):

    websites: list[ScrapedWebsite]



# =====================================================
# 7. COMPANY EXTRACTION SCHEMA
# =====================================================


class CompanyProfile(BaseModel):

    company_name: str | None

    website: str

    country: str | None

    description: str | None


    buyer_type: list[BuyerType]


    products: list[str]


    importing_activity: bool


    buying_signals: list[str]


    email: list[str]


    phone: list[str]


    address: str | None


    contact_page: str | None


    linkedin: str | None



class CompanyProfileList(BaseModel):

    companies: list[CompanyProfile]



# =====================================================
# 8. EMAIL ENRICHMENT SCHEMA
# =====================================================


class ContactInformation(BaseModel):

    company_name: str

    domain: str

    emails: list[str]

    verified_emails: list[str]

    contact_quality: float



class ContactInformationList(BaseModel):

    contacts: list[ContactInformation]



# =====================================================
# 9. DUPLICATE DETECTION SCHEMA
# =====================================================


class DuplicateCheck(BaseModel):

    company_name: str

    duplicate_found: bool

    matched_company: str | None

    similarity_score: float



# =====================================================
# 10. FINAL LEAD SCORING SCHEMA
# =====================================================


class LeadScore(BaseModel):

    company_name: str


    product_match_score: float


    buyer_type_score: float


    contact_score: float


    buying_intent_score: float


    company_quality_score: float


    final_score: float


    explanation: str



class LeadScoreList(BaseModel):

    leads: list[LeadScore]