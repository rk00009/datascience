# app/url_filter.py

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse, urlunparse

from app.schemas import (
    SERPResultList,
    URLClassification,
    URLClassificationList,
)


# ============================================================
# DOMAIN FILTERS
# ============================================================

BLACKLISTED_DOMAINS = {
    "google.com",
    "google.de",
    "bing.com",
    "yahoo.com",

    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "youtube.com",
    "tiktok.com",
    "twitter.com",
    "x.com",

    "wikipedia.org",
    "britannica.com",

    "amazon.com",
    "amazon.de",
    "ebay.com",
    "ebay.de",

    "alibaba.com",
    "aliexpress.com",
    "indiamart.com",
    "made-in-china.com",
    "globalsources.com",

    "tradewheel.com",
    "go4worldbusiness.com",
    "exportersindia.com",
    "exporthub.com",
    "ec21.com",
    "tradeindia.com",

    "globalbuyersonline.com",
    "exportbusinessmart.com",
    "volza.com",
    "tridge.com",
    "usetorg.com",

    "yellowpages.com",
    "yelp.com",
    "crunchbase.com",
    "zoominfo.com",
    "dnb.com",
}


LOW_QUALITY_DOMAINS = {
    "reddit.com",
    "quora.com",
    "medium.com",
}


# ============================================================
# URL PATTERNS
# ============================================================

BAD_URL_PATTERNS = [
    r"/search(?:/|$|\?)",
    r"/login(?:/|$|\?)",
    r"/signin(?:/|$|\?)",
    r"/register(?:/|$|\?)",
    r"/signup(?:/|$|\?)",
    r"/checkout(?:/|$|\?)",
    r"/account(?:/|$|\?)",
]


RETAIL_PATTERNS = [
    r"/cart",
    r"/checkout",
    r"/add-to-cart",
    r"/buy-now",
]


PRODUCT_PAGE_PATTERNS = [
    r"/product/",
    r"/products/",
    r"/shop/",
    r"/store/",
]


# ============================================================
# SIGNALS
# ============================================================

PRODUCT_SIGNALS = {
    "groundnut": 20,
    "groundnuts": 20,
    "peanut": 20,
    "peanuts": 20,
    "groundnut kernel": 20,
    "groundnut kernels": 20,
    "peanut kernel": 20,
    "peanut kernels": 20,
    "erdnuss": 20,
    "erdnüsse": 20,
    "erdnusskern": 20,
    "erdnusskerne": 20,
}


BUYER_SIGNALS = {
    "importer": 20,
    "importeur": 20,
    "import": 10,

    "wholesaler": 16,
    "wholesale": 16,
    "großhandel": 16,
    "grosshandel": 16,

    "distributor": 14,
    "distribution": 12,

    "food manufacturer": 15,
    "food processor": 15,
    "food industry": 12,

    "lebensmittelhersteller": 15,
    "lebensmittelindustrie": 12,

    "verarbeiter": 14,

    "trading company": 14,
    "trading": 10,
    "handelsunternehmen": 14,
    "handel": 10,

    "procurement": 10,
    "purchasing": 10,
    "einkauf": 10,
    "beschaffung": 10,

    "sourcing": 8,
    "rfq": 10,
}


COMPANY_SIGNALS = {
    "gmbh": 12,
    "gmbh & co": 14,
    "kg": 5,
    "ag": 7,
    "se": 7,
    "company": 5,
    "group": 4,

    "food": 5,
    "foods": 6,

    "trading": 8,
    "handel": 8,

    "import": 8,
    "importer": 10,
    "importeur": 10,

    "wholesale": 8,
    "großhandel": 8,
    "grosshandel": 8,

    "distributor": 8,
    "distribution": 7,

    "lebensmittel": 8,
    "manufacturer": 7,
    "verarbeiter": 7,
    "snack": 5,
}


SUPPLIER_TERMS = {
    "supplier",
    "suppliers",
    "exporter",
    "exporters",
    "bulk supplier",
}


# ============================================================
# HELPERS
# ============================================================

def _clean_text(value: Any) -> str:

    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value),
    ).strip()


def _get_value(
    item: Any,
    field: str,
    default: Any = "",
) -> Any:

    if isinstance(item, dict):
        return item.get(
            field,
            default,
        )

    return getattr(
        item,
        field,
        default,
    )


def _normalize_url(
    url: str,
) -> str:

    url = _clean_text(url)

    if not url:
        return ""

    if not url.startswith(
        (
            "http://",
            "https://",
        )
    ):
        url = "https://" + url

    try:

        parsed = urlparse(url)

        if not parsed.hostname:
            return ""

        hostname = parsed.hostname.lower()

        path = parsed.path or "/"

        if path != "/":
            path = path.rstrip("/")

        return urlunparse(
            (
                parsed.scheme.lower(),
                hostname,
                path,
                "",
                parsed.query,
                "",
            )
        )

    except Exception:

        return ""


def _get_domain(
    url: str,
) -> str:

    try:

        hostname = urlparse(
            url
        ).hostname

        if not hostname:
            return ""

        hostname = hostname.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        return hostname

    except Exception:

        return ""


def _domain_is_blocked(
    domain: str,
) -> bool:

    domain = domain.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    for blocked in BLACKLISTED_DOMAINS:

        if (
            domain == blocked
            or domain.endswith(
                "." + blocked
            )
        ):
            return True

    return False


def _matches_any(
    text: str,
    patterns: list[str],
) -> bool:

    for pattern in patterns:

        if re.search(
            pattern,
            text,
            re.IGNORECASE,
        ):
            return True

    return False


# ============================================================
# ACCEPT BOTH SERPResultList AND LIST
# ============================================================

def _normalize_serp_input(
    data: Any,
) -> list[Any]:

    if isinstance(
        data,
        SERPResultList,
    ):
        return list(
            data.results
        )

    if hasattr(
        data,
        "results",
    ):
        return list(
            data.results
        )

    if isinstance(
        data,
        (list, tuple),
    ):
        return list(data)

    if data is None:
        return []

    raise TypeError(
        "Expected SERPResultList or list, "
        f"got {type(data).__name__}"
    )


# ============================================================
# INFORMATION PAGE
# ============================================================

def _is_information_page(
    title: str,
    snippet: str,
) -> bool:

    text = (
        title + " " + snippet
    ).lower()

    information_terms = [
        "wikipedia",
        "encyclopedia",
        "market report",
        "market overview",
        "market analysis",
        "market trends",
        "health benefits",
        "nutrition facts",
        "nutritional value",
        "what are peanuts",
        "what is peanut",
    ]

    return any(
        term in text
        for term in information_terms
    )


# ============================================================
# SUPPLIER-ONLY
# ============================================================

def _is_supplier_only(
    title: str,
    snippet: str,
) -> bool:

    text = (
        title + " " + snippet
    ).lower()

    supplier_hits = sum(
        1
        for term in SUPPLIER_TERMS
        if term in text
    )

    buyer_hit = any(
        term in text
        for term in BUYER_SIGNALS
    )

    return (
        supplier_hits >= 2
        and not buyer_hit
    )


# ============================================================
# COMPANY TYPE
# ============================================================

def _infer_company_type(
    title: str,
    snippet: str,
) -> str | None:

    text = (
        title + " " + snippet
    ).lower()

    if any(
        x in text
        for x in [
            "importer",
            "importeur",
        ]
    ):
        return "importer"

    if any(
        x in text
        for x in [
            "distributor",
            "distribution",
            "händler",
            "handler",
        ]
    ):
        return "distributor"

    if any(
        x in text
        for x in [
            "wholesaler",
            "wholesale",
            "großhandel",
            "grosshandel",
        ]
    ):
        return "wholesaler"

    if any(
        x in text
        for x in [
            "food manufacturer",
            "food processor",
            "manufacturer",
            "lebensmittelhersteller",
            "lebensmittelindustrie",
            "verarbeiter",
            "snack manufacturer",
            "snackhersteller",
        ]
    ):
        return "food_processor"

    if any(
        x in text
        for x in [
            "trading company",
            "commodity trader",
            "trading",
            "handelsunternehmen",
            "handel",
        ]
    ):
        return "trading_company"

    return None


# ============================================================
# SCORE
# ============================================================

def _score_result(
    title: str,
    snippet: str,
    url: str,
    domain: str,
) -> tuple[int, str]:

    text = (
        title
        + " "
        + snippet
        + " "
        + url
        + " "
        + domain
    ).lower()

    score = 15

    reasons = []

    # Product
    product_score = 0

    for term, points in PRODUCT_SIGNALS.items():

        if term in text:

            product_score = max(
                product_score,
                points,
            )

    if product_score:

        score += product_score

        reasons.append(
            "product relevance"
        )

    # Buyer
    buyer_score = 0

    for term, points in BUYER_SIGNALS.items():

        if term in text:

            buyer_score += points

    buyer_score = min(
        buyer_score,
        45,
    )

    if buyer_score:

        score += buyer_score

        reasons.append(
            "buyer signals"
        )

    # Company
    company_score = 0

    for term, points in COMPANY_SIGNALS.items():

        if term in text:

            company_score += points

    company_score = min(
        company_score,
        25,
    )

    if company_score:

        score += company_score

        reasons.append(
            "company signals"
        )

    # Domain
    if domain.endswith(
        (
            ".de",
            ".com",
            ".eu",
            ".net",
            ".org",
        )
    ):

        score += 5

    # Supplier penalty
    supplier_hits = sum(
        1
        for term in SUPPLIER_TERMS
        if term in text
    )

    if supplier_hits:

        score -= min(
            15,
            supplier_hits * 5,
        )

        reasons.append(
            "supplier language"
        )

    # Product page penalty
    if _matches_any(
        url,
        PRODUCT_PAGE_PATTERNS,
    ):

        score -= 4

        reasons.append(
            "product page"
        )

    # Retail penalty
    if _matches_any(
        url,
        RETAIL_PATTERNS,
    ):

        score -= 20

        reasons.append(
            "retail page"
        )

    # Low quality
    if any(
        domain == x
        or domain.endswith(
            "." + x
        )
        for x in LOW_QUALITY_DOMAINS
    ):

        score -= 20

        reasons.append(
            "low quality domain"
        )

    score = max(
        0,
        min(
            score,
            100,
        )
    )

    if not reasons:

        reasons.append(
            "limited commercial signals"
        )

    return (
        score,
        ", ".join(reasons),
    )


# ============================================================
# MAIN FILTER
# ============================================================

def hard_filter_urls(
    serp_results: Any,
    minimum_score: int = 45,
) -> URLClassificationList:

    results = _normalize_serp_input(
        serp_results
    )

    stats = {
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
        "accepted": 0,
    }

    accepted = []

    seen = set()

    # ========================================================
    # PROCESS
    # ========================================================

    for item in results:

        raw_url = _get_value(
            item,
            "url",
            "",
        )

        title = _clean_text(
            _get_value(
                item,
                "title",
                "",
            )
        )

        snippet = _clean_text(
            _get_value(
                item,
                "snippet",
                "",
            )
        )

        url = _normalize_url(
            raw_url
        )

        # ----------------------------------------------------
        # URL
        # ----------------------------------------------------

        if not url:

            stats["invalid_url"] += 1

            continue

        parsed = urlparse(url)

        if (
            parsed.scheme
            not in {
                "http",
                "https",
            }
            or not parsed.netloc
        ):

            stats["invalid_url"] += 1

            continue

        # ----------------------------------------------------
        # DOMAIN
        # ----------------------------------------------------

        domain = _get_domain(
            url
        )

        if not domain:

            stats["invalid_domain"] += 1

            continue

        # ----------------------------------------------------
        # DUPLICATE
        # ----------------------------------------------------

        if url in seen:

            stats["duplicates"] += 1

            continue

        seen.add(url)

        # ----------------------------------------------------
        # BLACKLIST
        # ----------------------------------------------------

        if _domain_is_blocked(
            domain
        ):

            stats["blacklisted_domain"] += 1

            continue

        # ----------------------------------------------------
        # BAD URL
        # ----------------------------------------------------

        if _matches_any(
            url,
            BAD_URL_PATTERNS,
        ):

            stats["bad_url_pattern"] += 1

            continue

        # ----------------------------------------------------
        # INFORMATION PAGE
        # ----------------------------------------------------

        if _is_information_page(
            title,
            snippet,
        ):

            stats["information_page"] += 1

            continue

        # ----------------------------------------------------
        # RETAIL
        # ----------------------------------------------------

        if _matches_any(
            url,
            RETAIL_PATTERNS,
        ):

            stats["retail"] += 1

            continue

        # ----------------------------------------------------
        # SUPPLIER ONLY
        # ----------------------------------------------------

        if _is_supplier_only(
            title,
            snippet,
        ):

            stats["supplier_only"] += 1

            continue

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        score, reason = _score_result(
            title=title,
            snippet=snippet,
            url=url,
            domain=domain,
        )

        # ----------------------------------------------------
        # LOW SCORE
        # ----------------------------------------------------

        if score < minimum_score:

            stats["low_quality"] += 1

            continue

        # ----------------------------------------------------
        # COMPANY TYPE
        # ----------------------------------------------------

        company_type = _infer_company_type(
            title,
            snippet,
        )

        # ----------------------------------------------------
        # ACCEPT
        # ----------------------------------------------------

        accepted.append(
            URLClassification(
                url=url,
                domain=domain,

                is_company_candidate=True,

                # IMPORTANT:
                # main.py expects this field.
                is_lead=True,

                company_type=company_type,

                relevance_score=float(
                    score
                ),

                reason=reason,

                keep=True,
            )
        )

        stats["accepted"] += 1

    # ========================================================
    # SORT
    # ========================================================

    accepted.sort(
        key=lambda x:
            x.relevance_score,
        reverse=True,
    )

    # ========================================================
    # PRINT
    # ========================================================

    print()
    print(
        "=============================="
    )
    print(
        "HARD URL FILTER"
    )
    print(
        "=============================="
    )

    for key, value in stats.items():

        print(
            f"{key}: {value}"
        )

    # ========================================================
    # RETURN MODEL
    # ========================================================

    return URLClassificationList(
        results=accepted
    )


# ============================================================
# PUBLIC API
# ============================================================

def classify_urls(
    serp_results: Any,
    minimum_score: int = 45,
) -> URLClassificationList:

    return hard_filter_urls(
        serp_results,
        minimum_score,
    )


def filter_urls(
    serp_results: Any,
    minimum_score: int = 45,
) -> URLClassificationList:

    return hard_filter_urls(
        serp_results,
        minimum_score,
    )


def filter_serp_results(
    serp_results: Any,
    minimum_score: int = 45,
) -> URLClassificationList:

    return hard_filter_urls(
        serp_results,
        minimum_score,
    )


# ============================================================
# UTILITY
# ============================================================

def get_accepted_urls(
    classified: URLClassificationList,
) -> list[str]:

    return [
        item.url
        for item in classified.results
        if item.keep
    ]


def deduplicate_by_domain(
    classified: URLClassificationList,
) -> URLClassificationList:

    best = {}

    for item in classified.results:

        current = best.get(
            item.domain
        )

        if (
            current is None
            or item.relevance_score
            > current.relevance_score
        ):

            best[item.domain] = item

    results = list(
        best.values()
    )

    results.sort(
        key=lambda x:
            x.relevance_score,
        reverse=True,
    )

    return URLClassificationList(
        results=results
    )


def print_candidates(
    classified: URLClassificationList,
    limit: int = 25,
) -> None:

    print()
    print(
        "=============================="
    )
    print(
        "CANDIDATES"
    )
    print(
        "=============================="
    )

    if not classified.results:

        print(
            "No company candidates found."
        )

        return

    for index, result in enumerate(
        classified.results[:limit],
        start=1,
    ):

        print(
            f"\n{index}. {result.domain}"
        )

        print(
            f"URL: {result.url}"
        )

        print(
            f"Type: {result.company_type}"
        )

        print(
            f"Score: "
            f"{result.relevance_score:.0f}"
        )

        print(
            f"Lead: {result.is_lead}"
        )

        print(
            f"Reason: {result.reason}"
        )