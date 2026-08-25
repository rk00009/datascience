"""
app/url_filter.py

Hard URL filtering and company-candidate classification layer.

Responsibilities
----------------
1. Normalize SERP results.
2. Remove obviously useless URLs.
3. Reject information-only pages.
4. Reject retail/product-only pages.
5. Reject supplier-only pages when appropriate.
6. Reject marketplaces/listing platforms.
7. Detect company/business websites.
8. Score remaining URLs.
9. Return a stable URLClassificationList.

IMPORTANT
---------
This module does NOT perform company extraction.

It should only answer:

    "Is this URL worth crawling as a possible buyer/company?"

Company name, email, phone, address, importing activity, products,
buying signals, etc. belong to the crawler/extractor stage.
"""

from __future__ import annotations

import re
from typing import Any, Iterable
from urllib.parse import urlparse

from pydantic import BaseModel, Field


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MINIMUM_SCORE = 45

MAX_RESULTS = 50


# ============================================================
# DOMAIN LISTS
# ============================================================

# Domains that are almost never useful as direct company websites.
BLACKLISTED_DOMAINS = {
    # Search / social
    "google.com",
    "google.de",
    "bing.com",
    "yahoo.com",
    "duckduckgo.com",
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "youtube.com",
    "tiktok.com",

    # Wikipedia / reference
    "wikipedia.org",
    "wikimedia.org",

    # Marketplaces / general directories
    "amazon.com",
    "amazon.de",
    "ebay.com",
    "ebay.de",
    "alibaba.com",
    "aliexpress.com",
    "made-in-china.com",
    "indiamart.com",

    # Generic directories / databases
    "yellowpages.com",
    "yelp.com",
    "tripadvisor.com",
    "crunchbase.com",
    "zoominfo.com",
    "rocketreach.co",
    "dnb.com",
    "kompass.com",

    # Generic buyer/supplier portals
    "exportbusinessmart.com",
    "globalbuyersonline.com",
    "go4worldbusiness.com",
    "tradeindia.com",
    "tradewheel.com",
    "ec21.com",
    "ecplaza.net",
    "exporthub.com",

    # Market intelligence / shipment databases
    "volza.com",
    "trademap.org",
    "importyeti.com",
    "panjiva.com",
    "importgenius.com",

    # General content / health / blogs
    "medium.com",
    "quora.com",
    "reddit.com",
    "pinterest.com",
}


# Domains that can contain useful company listings,
# but should not automatically be treated as company websites.
LISTING_DOMAINS = {
    "lieferanten.de",
    "wer liefert was",
    "wlw.com",
    "europages.com",
    "industrystock.com",
    "foursquare.com",
}


# ============================================================
# URL PATTERNS
# ============================================================

BAD_URL_PATTERNS = [
    r"/login",
    r"/signin",
    r"/sign-in",
    r"/register",
    r"/signup",
    r"/cart",
    r"/checkout",
    r"/account",
    r"/password",
    r"/privacy",
    r"/cookie",
    r"/terms",
    r"/impressum/datenschutz",
]

INFORMATION_PATTERNS = [
    r"/blog/",
    r"/blog$",
    r"/news/",
    r"/news$",
    r"/article/",
    r"/articles/",
    r"/magazine/",
    r"/knowledge/",
    r"/guide/",
    r"/guides/",
    r"/market-report",
    r"/market-report/",
    r"/market-overview",
    r"/market-overview/",
    r"/research/",
    r"/report/",
    r"/reports/",
    r"/wiki/",
    r"/faq/",
]

RETAIL_PATTERNS = [
    r"/shop/",
    r"/shop$",
    r"/store/",
    r"/store$",
    r"/product/",
    r"/products/",
    r"/product$",
    r"/products$",
    r"/p/",
    r"/buy/",
    r"/buy$",
    r"/order/",
    r"/cart/",
]

MARKETPLACE_PATTERNS = [
    r"/marketplace/",
    r"/marketplace$",
    r"/suppliers/",
    r"/supplier/",
    r"/buyers/",
    r"/buyer/",
    r"/buy-requirements/",
    r"/buyrequirements/",
    r"/rfq/",
]

SUPPLIER_ONLY_TERMS = [
    "supplier",
    "exporter",
    "manufacturer",
    "seller",
    "wholesale supplier",
    "bulk supplier",
    "peanut exporter",
    "groundnut exporter",
    "peanuts exporter",
    "supplier of",
    "we supply",
    "we export",
]

BUYER_SIGNAL_TERMS = [
    "importer",
    "import",
    "procurement",
    "purchasing",
    "purchase",
    "purchasing department",
    "sourcing",
    "supply chain",
    "buyer",
    "buyers",
    "buying",
    "buy",
    "supplier requirement",
    "supplier requirements",
    "rfq",
    "request for quotation",
    "raw material",
    "ingredients",
    "food ingredients",
    "food industry",
    "wholesale",
    "wholesaler",
    "trading",
    "trader",
    "distribution",
    "distributor",
    "international trade",
    "commodity",
    "commodities",
    "imported",
    "imports",
]

COMPANY_TERMS = [
    "gmbh",
    "gmbh & co",
    "gmbh & co. kg",
    "ag",
    "kg",
    "se",
    "ltd",
    "limited",
    "inc",
    "corp",
    "corporation",
    "company",
    "co.",
    "group",
    "holding",
    "trading",
    "handel",
    "handels",
    "import",
    "distribution",
    "distributor",
    "wholesale",
    "wholesaler",
    "lebensmittel",
    "lebensmittelhandel",
    "lebensmittelhersteller",
    "lebensmittelindustrie",
    "food",
    "foodservice",
    "food ingredients",
    "ingredients",
    "agro",
    "agrar",
]

GENERIC_INFORMATION_TERMS = [
    "what are peanuts",
    "what is groundnut",
    "health benefits",
    "nutrition",
    "nutritional value",
    "calories",
    "vitamins",
    "benefits of",
    "how to",
    "recipe",
    "recipes",
    "definition",
]


# ============================================================
# MODELS
# ============================================================

class URLClassification(BaseModel):
    """
    Stable classification object.

    These fields are intentionally compatible with the rest
    of the pipeline.
    """

    url: str
    domain: str = ""

    is_company_candidate: bool = False
    is_lead: bool = False

    company_type: str | None = None

    relevance_score: float = 0
    reason: str = ""

    keep: bool = False

    # Extra metadata used by downstream stages.
    title: str | None = None
    snippet: str | None = None

    buyer_signal_score: float = 0
    company_signal_score: float = 0


class URLClassificationList(BaseModel):
    results: list[URLClassification] = Field(default_factory=list)


# ============================================================
# GENERAL HELPERS
# ============================================================

def _safe_str(value: Any) -> str:
    if value is None:
        return ""

    try:
        return str(value).strip()
    except Exception:
        return ""


def _normalize_domain(domain: str) -> str:
    domain = _safe_str(domain).lower().strip()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


def _domain_from_url(url: str) -> str:
    try:
        parsed = urlparse(url)

        domain = parsed.netloc.lower().strip()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain
    except Exception:
        return ""


def _base_domain(domain: str) -> str:
    """
    Converts:

        www.example.com -> example.com
        apps.example.com -> example.com

    This intentionally keeps this simple and avoids requiring
    tldextract as an external dependency.
    """

    domain = _normalize_domain(domain)

    parts = domain.split(".")

    if len(parts) <= 2:
        return domain

    # Common German / UK second-level domains.
    if len(parts) >= 3 and parts[-2] in {
        "co",
        "com",
        "org",
        "net",
        "gov",
        "ac",
    }:
        return ".".join(parts[-3:])

    return ".".join(parts[-2:])


def _full_text(item: Any) -> str:
    """
    Extract searchable text from common SERP result structures.
    """

    pieces: list[str] = []

    if isinstance(item, dict):
        for key in (
            "title",
            "snippet",
            "description",
            "content",
            "text",
            "source",
            "displayed_link",
            "domain",
        ):
            value = item.get(key)

            if value:
                pieces.append(_safe_str(value))

    else:
        for attr in (
            "title",
            "snippet",
            "description",
            "content",
            "text",
            "source",
            "displayed_link",
            "domain",
        ):
            try:
                value = getattr(item, attr, None)
            except Exception:
                value = None

            if value:
                pieces.append(_safe_str(value))

    return " ".join(pieces).lower()


def _get_value(item: Any, *keys: str) -> str:
    for key in keys:
        if isinstance(item, dict):
            value = item.get(key)
        else:
            try:
                value = getattr(item, key, None)
            except Exception:
                value = None

        if value is not None and _safe_str(value):
            return _safe_str(value)

    return ""


def _get_url(item: Any) -> str:
    return _get_value(
        item,
        "url",
        "link",
        "href",
        "target_url",
    )


def _get_title(item: Any) -> str:
    return _get_value(
        item,
        "title",
        "name",
    )


def _get_snippet(item: Any) -> str:
    return _get_value(
        item,
        "snippet",
        "description",
        "content",
        "text",
    )


# ============================================================
# SERP NORMALIZATION
# ============================================================

def _normalize_serp_results(serp_results: Any) -> list[Any]:
    """
    Handles:

        list
        tuple
        SERPResultList
        objects containing .results
        objects containing .items
        dictionaries containing results/items
    """

    if serp_results is None:
        return []

    if isinstance(serp_results, (list, tuple)):
        return list(serp_results)

    if isinstance(serp_results, dict):
        for key in (
            "results",
            "items",
            "organic_results",
            "data",
        ):
            value = serp_results.get(key)

            if isinstance(value, (list, tuple)):
                return list(value)

        return [serp_results]

    for attr in (
        "results",
        "items",
        "organic_results",
        "data",
    ):
        try:
            value = getattr(serp_results, attr, None)
        except Exception:
            value = None

        if isinstance(value, (list, tuple)):
            return list(value)

    # Last-resort iterable handling.
    try:
        if not isinstance(serp_results, (str, bytes)):
            return list(serp_results)
    except Exception:
        pass

    return []


# ============================================================
# SEARCH PLAN HELPERS
# ============================================================

def _get_search_plan_value(
    search_plan: Any,
    key: str,
    default: Any = None,
) -> Any:

    if search_plan is None:
        return default

    if isinstance(search_plan, dict):
        return search_plan.get(key, default)

    try:
        return getattr(search_plan, key, default)
    except Exception:
        return default


def _infer_target_market(
    results: list[Any],
    search_plan: Any = None,
) -> str | None:

    explicit = _get_search_plan_value(
        search_plan,
        "target_market",
    )

    if explicit:
        return _safe_str(explicit)

    return None


def _get_product_terms(search_plan: Any) -> list[str]:
    terms: list[str] = []

    product = _get_search_plan_value(
        search_plan,
        "product",
    )

    if product:
        terms.append(_safe_str(product).lower())

    synonyms = _get_search_plan_value(
        search_plan,
        "product_synonyms",
        [],
    )

    if isinstance(synonyms, (list, tuple)):
        for item in synonyms:
            text = _safe_str(item).lower()

            if text:
                terms.append(text)

    return list(dict.fromkeys(terms))


# ============================================================
# DOMAIN CLASSIFICATION
# ============================================================

def _is_blacklisted_domain(domain: str) -> bool:
    base = _base_domain(domain)

    if not base:
        return True

    if base in BLACKLISTED_DOMAINS:
        return True

    for blocked in BLACKLISTED_DOMAINS:
        if base.endswith("." + blocked):
            return True

    return False


def _is_listing_domain(domain: str) -> bool:
    base = _base_domain(domain)

    if base in LISTING_DOMAINS:
        return True

    for listing in LISTING_DOMAINS:
        if base.endswith("." + listing):
            return True

    return False


# ============================================================
# URL VALIDATION
# ============================================================

def _valid_url(url: str) -> bool:
    if not url:
        return False

    try:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return False

        if not parsed.netloc:
            return False

        domain = parsed.netloc.lower()

        if "." not in domain:
            return False

        return True

    except Exception:
        return False


def _matches_pattern(url: str, patterns: Iterable[str]) -> bool:
    lower = url.lower()

    for pattern in patterns:
        try:
            if re.search(pattern, lower):
                return True
        except re.error:
            continue

    return False


# ============================================================
# CONTENT CLASSIFICATION
# ============================================================

def _contains_any(text: str, terms: Iterable[str]) -> list[str]:
    found: list[str] = []

    lower = text.lower()

    for term in terms:
        if term.lower() in lower:
            found.append(term)

    return found


def _is_information_page(url: str, text: str) -> bool:
    if _matches_pattern(url, INFORMATION_PATTERNS):
        return True

    found = _contains_any(
        text,
        GENERIC_INFORMATION_TERMS,
    )

    # Do not reject a company merely because one generic word appears.
    return len(found) >= 2


def _is_retail_page(url: str, text: str) -> bool:
    if _matches_pattern(url, RETAIL_PATTERNS):
        return True

    retail_terms = [
        "add to cart",
        "shopping cart",
        "buy now",
        "price",
        "€",
        "$",
        "in stock",
        "checkout",
    ]

    found = _contains_any(text, retail_terms)

    return len(found) >= 4


def _is_marketplace_page(url: str, text: str) -> bool:
    if _matches_pattern(url, MARKETPLACE_PATTERNS):
        return True

    marketplace_terms = [
        "browse suppliers",
        "verified suppliers",
        "supplier directory",
        "buyer requirements",
        "buy requirements",
        "post your requirement",
        "supplier marketplace",
    ]

    found = _contains_any(text, marketplace_terms)

    return len(found) >= 2


def _is_supplier_only(text: str) -> bool:
    supplier_hits = _contains_any(
        text,
        SUPPLIER_ONLY_TERMS,
    )

    buyer_hits = _contains_any(
        text,
        BUYER_SIGNAL_TERMS,
    )

    # Supplier-only pages should only be rejected when there
    # is strong supplier language AND no meaningful buyer signal.
    if len(supplier_hits) >= 2 and not buyer_hits:
        return True

    return False


# ============================================================
# SCORING
# ============================================================

def _score_company_signals(
    domain: str,
    title: str,
    snippet: str,
    search_plan: Any,
) -> tuple[float, list[str]]:

    text = f"{domain} {title} {snippet}".lower()

    score = 0.0
    reasons: list[str] = []

    company_hits = _contains_any(
        text,
        COMPANY_TERMS,
    )

    # Company/legal entity signals.
    if company_hits:
        score += min(35, len(company_hits) * 8)
        reasons.append(
            "company/business signals: "
            + ", ".join(company_hits[:5])
        )

    # Corporate-looking domain.
    if domain:
        score += 10

    # Company pages tend to have contact/legal pages,
    # but we only score the SERP evidence here.
    corporate_terms = [
        "about us",
        "contact",
        "our company",
        "unternehmen",
        "über uns",
        "kontakt",
        "standorte",
        "locations",
    ]

    corporate_hits = _contains_any(
        text,
        corporate_terms,
    )

    if corporate_hits:
        score += min(15, len(corporate_hits) * 5)

    return score, reasons


def _score_buyer_signals(
    text: str,
    search_plan: Any,
) -> tuple[float, list[str]]:

    score = 0.0
    reasons: list[str] = []

    buyer_hits = _contains_any(
        text,
        BUYER_SIGNAL_TERMS,
    )

    if buyer_hits:
        score += min(50, len(buyer_hits) * 10)

        reasons.append(
            "buyer signals: "
            + ", ".join(buyer_hits[:7])
        )

    # Product relevance.
    product_terms = _get_product_terms(
        search_plan
    )

    product_hits = []

    for product in product_terms:
        if product and product in text:
            product_hits.append(product)

    if product_hits:
        score += min(25, len(product_hits) * 8)

        reasons.append(
            "product relevance: "
            + ", ".join(product_hits[:5])
        )

    # Target market.
    target_market = _get_search_plan_value(
        search_plan,
        "target_market",
    )

    if target_market:
        market = _safe_str(target_market).lower()

        if market and market in text:
            score += 15
            reasons.append(
                f"target market signal: {target_market}"
            )

        # Germany-specific language signals.
        if market == "germany":
            german_hits = _contains_any(
                text,
                [
                    "deutschland",
                    "germany",
                    "de",
                    "gmbh",
                    "ag",
                ],
            )

            if german_hits:
                score += min(
                    10,
                    len(german_hits) * 5,
                )

    return score, reasons


def _determine_company_type(text: str) -> str:
    lower = text.lower()

    if any(
        term in lower
        for term in [
            "importer",
            "import",
            "importeur",
            "importeur deutschland",
        ]
    ):
        return "importer"

    if any(
        term in lower
        for term in [
            "distributor",
            "distribution",
            "distribution company",
            "händler",
            "handel",
        ]
    ):
        return "distributor"

    if any(
        term in lower
        for term in [
            "wholesaler",
            "wholesale",
            "großhandel",
            "grosshandel",
        ]
    ):
        return "wholesaler"

    if any(
        term in lower
        for term in [
            "manufacturer",
            "manufacturer",
            "food manufacturer",
            "food processor",
            "lebensmittelhersteller",
            "hersteller",
        ]
    ):
        return "food_processor"

    if any(
        term in lower
        for term in [
            "trading company",
            "trader",
            "commodity",
            "handelsunternehmen",
            "handelsgesellschaft",
        ]
    ):
        return "trading_company"

    return "company"


# ============================================================
# SINGLE URL CLASSIFICATION
# ============================================================

def classify_single_url(
    item: Any,
    search_plan: Any = None,
    target_market: str | None = None,
) -> URLClassification:

    url = _get_url(item)
    title = _get_title(item)
    snippet = _get_snippet(item)

    domain = _domain_from_url(url)

    text = (
        f"{domain} "
        f"{title} "
        f"{snippet} "
        f"{url}"
    ).lower()

    # --------------------------------------------------------
    # Invalid URL
    # --------------------------------------------------------

    if not _valid_url(url):

        return URLClassification(
            url=url,
            domain=domain,
            is_company_candidate=False,
            is_lead=False,
            relevance_score=0,
            reason="invalid URL",
            keep=False,
            title=title or None,
            snippet=snippet or None,
        )

    # --------------------------------------------------------
    # Blacklisted domain
    # --------------------------------------------------------

    if _is_blacklisted_domain(domain):

        return URLClassification(
            url=url,
            domain=domain,
            is_company_candidate=False,
            is_lead=False,
            relevance_score=0,
            reason="blacklisted domain",
            keep=False,
            title=title or None,
            snippet=snippet or None,
        )

    # --------------------------------------------------------
    # Bad URL
    # --------------------------------------------------------

    if _matches_pattern(
        url,
        BAD_URL_PATTERNS,
    ):

        return URLClassification(
            url=url,
            domain=domain,
            is_company_candidate=False,
            is_lead=False,
            relevance_score=0,
            reason="bad URL pattern",
            keep=False,
            title=title or None,
            snippet=snippet or None,
        )

    # --------------------------------------------------------
    # Information page
    # --------------------------------------------------------

    if _is_information_page(
        url,
        text,
    ):

        return URLClassification(
            url=url,
            domain=domain,
            is_company_candidate=False,
            is_lead=False,
            relevance_score=0,
            reason="information page",
            keep=False,
            title=title or None,
            snippet=snippet or None,
        )

    # --------------------------------------------------------
    # Marketplace
    # --------------------------------------------------------

    if _is_marketplace_page(
        url,
        text,
    ):

        return URLClassification(
            url=url,
            domain=domain,
            is_company_candidate=False,
            is_lead=False,
            relevance_score=0,
            reason="listing/marketplace page",
            keep=False,
            title=title or None,
            snippet=snippet or None,
        )

    # --------------------------------------------------------
    # Retail
    # --------------------------------------------------------

    if _is_retail_page(
        url,
        text,
    ):

        return URLClassification(
            url=url,
            domain=domain,
            is_company_candidate=False,
            is_lead=False,
            relevance_score=0,
            reason="retail/product page",
            keep=False,
            title=title or None,
            snippet=snippet or None,
        )

    # --------------------------------------------------------
    # Listing domain
    # --------------------------------------------------------

    listing_domain = _is_listing_domain(domain)

    # --------------------------------------------------------
    # Supplier-only detection
    # --------------------------------------------------------

    supplier_only = _is_supplier_only(text)

    # --------------------------------------------------------
    # Scoring
    # --------------------------------------------------------

    company_score, company_reasons = (
        _score_company_signals(
            domain=domain,
            title=title,
            snippet=snippet,
            search_plan=search_plan,
        )
    )

    # If caller explicitly supplied target market,
    # temporarily inject it into scoring without mutating
    # the user's search plan.
    scoring_plan = search_plan

    if target_market and search_plan is None:
        scoring_plan = {
            "target_market": target_market
        }

    buyer_score, buyer_reasons = (
        _score_buyer_signals(
            text=text,
            search_plan=scoring_plan,
        )
    )

    score = company_score + buyer_score

    # Listing domains are allowed if they contain strong
    # company/buyer evidence. They simply receive a penalty.
    if listing_domain:
        score -= 20

    if supplier_only:
        score -= 35

    # --------------------------------------------------------
    # Company candidate decision
    # --------------------------------------------------------

    company_candidate = (
        score >= 40
        or buyer_score >= 25
        or company_score >= 20
    )

    # Strong supplier-only pages are not buyer candidates.
    if supplier_only and buyer_score < 30:
        company_candidate = False

    # Generic information websites should never survive.
    if _contains_any(
        text,
        GENERIC_INFORMATION_TERMS,
    ) and buyer_score < 20:
        company_candidate = False

    # --------------------------------------------------------
    # Lead decision
    # --------------------------------------------------------

    # A lead is NOT necessarily a confirmed buyer.
    # It means "worth crawling".
    is_lead = (
        company_candidate
        and score >= 45
    )

    # Strong importer / buyer signal can override
    # mediocre company wording.
    if buyer_score >= 40 and not supplier_only:
        is_lead = True

    # --------------------------------------------------------
    # Reason
    # --------------------------------------------------------

    reasons = []

    reasons.extend(company_reasons)
    reasons.extend(buyer_reasons)

    if listing_domain:
        reasons.append(
            "listing/directory domain"
        )

    if supplier_only:
        reasons.append(
            "supplier-only language detected"
        )

    if not reasons:
        reasons.append(
            "general business/company candidate"
        )

    reason = "; ".join(reasons)

    company_type = _determine_company_type(
        text
    )

    return URLClassification(
        url=url,
        domain=domain,
        is_company_candidate=company_candidate,
        is_lead=is_lead,
        company_type=company_type,
        relevance_score=max(0, round(score, 2)),
        reason=reason,
        keep=is_lead,
        title=title or None,
        snippet=snippet or None,
        buyer_signal_score=round(
            buyer_score,
            2,
        ),
        company_signal_score=round(
            company_score,
            2,
        ),
    )


# ============================================================
# HARD FILTER
# ============================================================

def hard_filter_urls(
    serp_results: Any,
    minimum_score: int = DEFAULT_MINIMUM_SCORE,
    search_plan: Any = None,
    target_market: str | None = None,
) -> URLClassificationList:

    results = _normalize_serp_results(
        serp_results
    )

    output: list[URLClassification] = []

    seen_urls: set[str] = set()
    seen_domains: set[str] = set()

    counters = {
        "total": len(results),
        "invalid_url": 0,
        "invalid_domain": 0,
        "blacklisted_domain": 0,
        "bad_url_pattern": 0,
        "information_page": 0,
        "listing_platform": 0,
        "product_listing_page": 0,
        "supplier_only": 0,
        "retail": 0,
        "low_quality": 0,
        "duplicates": 0,
    }

    print()
    print("==============================")
    print("HARD URL FILTER")
    print("==============================")

    if target_market:
        print(
            f"Target market: {target_market}"
        )

    for item in results:

        url = _get_url(item)

        normalized_url = (
            url.strip().lower().rstrip("/")
            if url
            else ""
        )

        if not normalized_url:
            counters["invalid_url"] += 1
            continue

        if normalized_url in seen_urls:
            counters["duplicates"] += 1
            continue

        seen_urls.add(normalized_url)

        domain = _domain_from_url(url)

        if not domain:
            counters["invalid_domain"] += 1
            continue

        base = _base_domain(domain)

        if base in seen_domains:
            # Don't aggressively remove all same-domain results.
            # Keep the first strong result only.
            counters["duplicates"] += 1
            continue

        result = classify_single_url(
            item=item,
            search_plan=search_plan,
            target_market=target_market,
        )

        reason = result.reason.lower()

        if "invalid url" in reason:
            counters["invalid_url"] += 1
            continue

        if "blacklisted domain" in reason:
            counters["blacklisted_domain"] += 1
            continue

        if "bad url pattern" in reason:
            counters["bad_url_pattern"] += 1
            continue

        if "information page" in reason:
            counters["information_page"] += 1
            continue

        if "listing/marketplace" in reason:
            counters["listing_platform"] += 1
            continue

        if "retail/product" in reason:
            counters["retail"] += 1
            continue

        if (
            "supplier-only" in reason
            and result.buyer_signal_score < 30
        ):
            counters["supplier_only"] += 1
            continue

        # Low-quality results are discarded.
        if result.relevance_score < minimum_score:
            counters["low_quality"] += 1
            continue

        # Only now mark the domain as seen.
        seen_domains.add(base)

        result.keep = True
        result.is_lead = True

        output.append(result)

    # Sort strongest candidates first.
    output.sort(
        key=lambda x: (
            x.relevance_score,
            x.buyer_signal_score,
            x.company_signal_score,
        ),
        reverse=True,
    )

    if len(output) > MAX_RESULTS:
        output = output[:MAX_RESULTS]

    print(
        f"total: {counters['total']}"
    )
    print(
        f"invalid_url: {counters['invalid_url']}"
    )
    print(
        f"invalid_domain: {counters['invalid_domain']}"
    )
    print(
        f"blacklisted_domain: "
        f"{counters['blacklisted_domain']}"
    )
    print(
        f"bad_url_pattern: "
        f"{counters['bad_url_pattern']}"
    )
    print(
        f"information_page: "
        f"{counters['information_page']}"
    )
    print(
        f"listing_platform: "
        f"{counters['listing_platform']}"
    )
    print(
        f"product_listing_page: "
        f"{counters['product_listing_page']}"
    )
    print(
        f"supplier_only: "
        f"{counters['supplier_only']}"
    )
    print(
        f"retail: "
        f"{counters['retail']}"
    )
    print(
        f"low_quality: "
        f"{counters['low_quality']}"
    )
    print(
        f"duplicates: "
        f"{counters['duplicates']}"
    )
    print(
        f"accepted: {len(output)}"
    )

    return URLClassificationList(
        results=output
    )


# ============================================================
# PUBLIC API
# ============================================================

def classify_urls(
    serp_results: Any,
    search_plan: Any = None,
    minimum_score: int = DEFAULT_MINIMUM_SCORE,
    target_market: str | None = None,
) -> URLClassificationList:

    return hard_filter_urls(
        serp_results=serp_results,
        minimum_score=minimum_score,
        search_plan=search_plan,
        target_market=target_market,
    )


def filter_urls(
    serp_results: Any,
    minimum_score: int = DEFAULT_MINIMUM_SCORE,
    search_plan: Any = None,
    target_market: str | None = None,
) -> URLClassificationList:

    return hard_filter_urls(
        serp_results=serp_results,
        minimum_score=minimum_score,
        search_plan=search_plan,
        target_market=target_market,
    )


def filter_serp_results(
    serp_results: Any,
    minimum_score: int = DEFAULT_MINIMUM_SCORE,
    search_plan: Any = None,
    target_market: str | None = None,
) -> URLClassificationList:

    return hard_filter_urls(
        serp_results=serp_results,
        minimum_score=minimum_score,
        search_plan=search_plan,
        target_market=target_market,
    )


# ============================================================
# OPTIONAL COMPATIBILITY ALIAS
# ============================================================

URLFilterResult = URLClassification
URLFilterResultList = URLClassificationList


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    test_results = [
        {
            "title": "Example Peanut Importer GmbH",
            "link": "https://example.de",
            "snippet": (
                "German importer and wholesaler of "
                "peanuts and groundnut kernels."
            ),
        },
        {
            "title": "Peanut Health Benefits",
            "link": "https://example-health.com/blog/peanuts",
            "snippet": (
                "Health benefits and nutritional value "
                "of peanuts."
            ),
        },
        {
            "title": "Peanuts Wholesale Supplier",
            "link": "https://supplier.example.com",
            "snippet": (
                "Leading peanut exporter and bulk supplier."
            ),
        },
    ]

    result = filter_serp_results(
        test_results,
        target_market="Germany",
        search_plan={
            "product": "groundnut",
            "product_synonyms": [
                "peanuts",
                "groundnut kernels",
                "peanut kernels",
            ],
            "target_market": "Germany",
        },
    )

    print()
    print("==============================")
    print("TEST RESULTS")
    print("==============================")

    for item in result.results:
        print(
            item.model_dump_json(
                indent=2
            )
        )