from urllib.parse import urlparse, urlunparse


# ============================================================
# DOMAIN BLACKLIST
# ============================================================

BLACKLISTED_DOMAINS = {

    # --------------------------------------------------------
    # B2B MARKETPLACES / DIRECTORIES
    # --------------------------------------------------------

    "tradekey.com",
    "tradewheel.com",
    "go4worldbusiness.com",
    "alibaba.com",
    "made-in-china.com",
    "indiamart.com",
    "exportersindia.com",
    "ec21.com",
    "ecplaza.net",
    "globalsources.com",
    "tradeindia.com",
    "e-worldtrade.com",
    "exporthub.com",
    "b2bmap.com",
    "usetorg.com",

    # --------------------------------------------------------
    # TRADE / IMPORT DATA PLATFORMS
    # --------------------------------------------------------

    "volza.com",
    "tridge.com",
    "importyeti.com",
    "importgenius.com",
    "panjiva.com",
    "datamyne.com",
    "descartes.com",

    # --------------------------------------------------------
    # MARKET RESEARCH / INFORMATION
    # --------------------------------------------------------

    "freshdi.com",
    "cbi.eu",
    "statista.com",
    "grandviewresearch.com",
    "mordorintelligence.com",
    "fortunebusinessinsights.com",
    "researchandmarkets.com",
    "marketresearch.com",

    # --------------------------------------------------------
    # GOVERNMENT / REPORT SOURCES
    # --------------------------------------------------------

    "usda.gov",
    "apps.fas.usda.gov",
    "europa.eu",
    "ec.europa.eu",
    "gov.uk",
    "bund.de",

    # --------------------------------------------------------
    # GENERAL INFORMATION
    # --------------------------------------------------------

    "wikipedia.org",
    "wikimedia.org",
    "britannica.com",

    # --------------------------------------------------------
    # SOCIAL MEDIA
    # --------------------------------------------------------

    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "youtube.com",
    "tiktok.com",

    # --------------------------------------------------------
    # ECOMMERCE
    # --------------------------------------------------------

    "amazon.com",
    "amazon.de",
    "ebay.com",
    "ebay.de",
    "walmart.com",
    "etsy.com",

    # --------------------------------------------------------
    # RETAIL
    # --------------------------------------------------------

    "nusskauf.de",

    # --------------------------------------------------------
    # NEWS / MEDIA
    # --------------------------------------------------------

    "reuters.com",
    "forbes.com",
    "bloomberg.com",
    "bbc.com",
    "cnn.com",

    # --------------------------------------------------------
    # JOBS
    # --------------------------------------------------------

    "indeed.com",
    "glassdoor.com",
    "stepstone.de",
    "monster.com",

    # --------------------------------------------------------
    # GENERAL DIRECTORIES / REVIEWS
    # --------------------------------------------------------

    "yellowpages.com",
    "yelp.com",
    "tripadvisor.com",
}


# ============================================================
# URL NORMALIZATION
# ============================================================

def normalize_url(url: str) -> str:

    if not url:
        return ""

    try:

        url = url.strip()

        if not url:
            return ""

        parsed = urlparse(url)

        if not parsed.scheme:
            url = "https://" + url
            parsed = urlparse(url)

        if not parsed.netloc:
            return ""

        return urlunparse(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path.rstrip("/"),
                "",
                "",
                "",
            )
        )

    except Exception:

        return ""


# ============================================================
# DOMAIN NORMALIZATION
# ============================================================

def normalize_domain(url: str) -> str:

    if not url:
        return ""

    try:

        parsed = urlparse(url)

        domain = (
            parsed.netloc
            .lower()
            .strip()
        )

        if domain.startswith("www."):
            domain = domain[4:]

        domain = domain.split(":")[0]

        return domain

    except Exception:

        return ""


# ============================================================
# BLACKLIST CHECK
# ============================================================

def is_blacklisted_domain(
    domain: str
) -> bool:

    if not domain:
        return True

    domain = domain.lower()

    if domain in BLACKLISTED_DOMAINS:
        return True

    for blocked in BLACKLISTED_DOMAINS:

        if domain.endswith(
            "." + blocked
        ):
            return True

    return False


# ============================================================
# BAD URL PATTERN
# ============================================================

def has_bad_url_pattern(
    url: str
) -> bool:

    if not url:
        return True

    url_lower = url.lower()

    bad_patterns = [

        # Authentication
        "/login",
        "/signin",
        "/sign-in",
        "/signup",
        "/sign-up",
        "/register",

        # Search pages
        "/search",
        "?q=",
        "?query=",
        "?search=",

        # Ecommerce
        "/cart",
        "/checkout",
        "/wishlist",

        # Jobs
        "/jobs",
        "/careers",
        "/career",
        "/vacancy",
        "/vacancies",

        # Forums
        "/forum",
        "/forums",
        "/community",

        # Files
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".mp4",
        ".avi",

    ]

    return any(
        pattern in url_lower
        for pattern in bad_patterns
    )


# ============================================================
# INFORMATION / ARTICLE DETECTION
# ============================================================

def looks_like_information_page(
    title: str,
    snippet: str
) -> bool:

    text = (
        (title or "")
        + " "
        + (snippet or "")
    ).lower()

    information_terms = [

        # Market research
        "market report",
        "market overview",
        "market update",
        "market analysis",
        "market trends",
        "market research",
        "industry report",
        "industry analysis",
        "research report",

        # Trade data
        "import data",
        "export data",
        "trade data",
        "import statistics",
        "export statistics",
        "shipment data",
        "trade statistics",
        "import shipments",
        "export shipments",

        # Market information
        "market entry",
        "market size",
        "market forecast",
        "price trends",
        "price analysis",

        # Educational content
        "what is",
        "what are",
        "how to",
        "guide to",
        "complete guide",
        "explained",

        # Health / nutrition
        "health benefits",
        "benefits of",
        "nutrition",
        "nutritional",
        "calories",
        "vitamins",
        "minerals",
        "superfood",
        "healthy snack",

        # Recipes
        "recipe",
        "recipes",
        "cooking",

        # Encyclopedia
        "wikipedia",
        "encyclopedia",

        # Supplier/listing articles
        "supplier list",
        "supplier directory",
        "suppliers directory",
        "top suppliers",
        "best suppliers",
        "manufacturers list",
        "manufacturer list",
        "manufacturer directory",
        "buyer directory",
        "buyers directory",
        "company directory",
        "business directory",
        "product directory",

    ]

    return any(
        term in text
        for term in information_terms
    )


# ============================================================
# LISTING / MARKETPLACE PAGE DETECTION
# ============================================================

def looks_like_listing_platform(
    title: str,
    snippet: str,
    url: str
) -> bool:

    text = (
        (title or "")
        + " "
        + (snippet or "")
        + " "
        + (url or "")
    ).lower()

    listing_terms = [

        "lists suppliers",
        "list suppliers",
        "list of suppliers",
        "supplier list",
        "supplier directory",
        "suppliers directory",

        "top suppliers",
        "best suppliers",
        "find suppliers",

        "find buyers",
        "buyer directory",
        "buyers directory",

        "manufacturer directory",
        "manufacturer list",

        "company directory",
        "business directory",
        "product directory",

        "compare suppliers",
        "compare manufacturers",

        "supplier database",
        "buyer database",

        "supplier marketplace",
        "b2b marketplace",

    ]

    return any(
        term in text
        for term in listing_terms
    )


# ============================================================
# PRODUCT / CATEGORY LISTING PAGE
# ============================================================

def looks_like_product_listing_page(
    url: str
) -> bool:

    if not url:
        return False

    url_lower = url.lower()

    product_patterns = [

        "/products/",
        "/product/",
        "/category/",
        "/categories/",
        "/shop/",
        "/store/",
        "/catalog/",
        "/catalogue/",
        "/collections/",
        "/marketplace/",
        "/suppliers/",
        "/supplier/",
        "/brands/",
        "/brand/",

    ]

    return any(
        pattern in url_lower
        for pattern in product_patterns
    )


# ============================================================
# SUPPLIER-ONLY DETECTION
# ============================================================

def looks_like_supplier_only(
    title: str,
    snippet: str
) -> bool:

    text = (
        (title or "")
        + " "
        + (snippet or "")
    ).lower()

    supplier_terms = [

        "supplier",
        "suppliers",
        "exporter",
        "exporters",
        "peanut exporter",
        "groundnut exporter",
        "bulk peanut exporter",
        "bulk groundnut exporter",
        "leading exporter",
        "manufacturer and exporter",
        "we export",
        "we supply",

    ]

    buyer_terms = [

        "buyer",
        "buyers",
        "buying",
        "purchase",
        "purchasing",
        "procurement",
        "sourcing",
        "importer",
        "import",
        "wholesaler",
        "wholesale",
        "distributor",

        # German
        "einkauf",
        "beschaffung",
        "importeur",
        "großhandel",
        "grosshandel",
        "lieferant gesucht",

    ]

    has_supplier_signal = any(
        term in text
        for term in supplier_terms
    )

    has_buyer_signal = any(
        term in text
        for term in buyer_terms
    )

    return (
        has_supplier_signal
        and not has_buyer_signal
    )


# ============================================================
# RETAIL DETECTION
# ============================================================

def looks_like_retail(
    title: str,
    snippet: str,
    url: str
) -> bool:

    text = (
        (title or "")
        + " "
        + (snippet or "")
        + " "
        + (url or "")
    ).lower()

    retail_terms = [

        "buy online",
        "order online",
        "online shop",
        "online store",
        "shop now",
        "add to cart",
        "add-to-cart",
        "shopping cart",
        "price per kg",
        "€ / kg",
        "eur/kg",
        "retail price",
        "for consumers",
        "consumer product",

    ]

    return any(
        term in text
        for term in retail_terms
    )


# ============================================================
# COMPANY SIGNAL
# ============================================================

def has_company_signal(
    title: str,
    snippet: str
) -> bool:

    text = (
        (title or "")
        + " "
        + (snippet or "")
    ).lower()

    company_terms = [

        # Legal entity signals
        "gmbh",
        "gmbh & co",
        "kg",
        "ltd",
        "limited",
        "inc",
        "corp",
        "corporation",
        "company",
        "group",

        # Commercial signals
        "food company",
        "food ingredients",
        "food industry",
        "ingredients",
        "trading company",
        "trading",
        "importer",
        "import",
        "wholesale",
        "wholesaler",
        "distributor",
        "manufacturer",
        "producer",
        "processor",
        "processing",

        # German
        "unternehmen",
        "importeur",
        "großhandel",
        "grosshandel",
        "händler",
        "haendler",
        "hersteller",
        "verarbeiter",
        "lebensmittel",
        "lebensmittelhersteller",

    ]

    return any(
        term in text
        for term in company_terms
    )


# ============================================================
# BUYER SIGNAL
# ============================================================

def has_buyer_signal(
    title: str,
    snippet: str
) -> bool:

    text = (
        (title or "")
        + " "
        + (snippet or "")
    ).lower()

    buyer_terms = [

        # English
        "procurement",
        "procurement department",
        "purchasing",
        "purchasing department",
        "purchase",
        "purchasing team",
        "sourcing",
        "supplier requirement",
        "supplier requirements",
        "buying",
        "buyer",
        "buyers",
        "importer",
        "import",
        "wholesaler",
        "wholesale",
        "distributor",
        "manufacturer",
        "processor",
        "raw material",
        "raw materials",
        "ingredients",

        # German
        "einkauf",
        "einkaufsabteilung",
        "beschaffung",
        "lieferant",
        "lieferanten",
        "lieferanten gesucht",
        "importeur",
        "großhandel",
        "grosshandel",
        "rohstoff",
        "rohstoffe",
        "lebensmittelhersteller",
        "verarbeiter",

    ]

    return any(
        term in text
        for term in buyer_terms
    )


# ============================================================
# TARGET MARKET SIGNAL
# ============================================================

def has_target_country_signal(
    title: str,
    snippet: str,
    target_market: str
) -> bool:

    if not target_market:
        return False

    text = (
        (title or "")
        + " "
        + (snippet or "")
    ).lower()

    country = (
        target_market
        .lower()
        .strip()
    )

    country_aliases = {

        "germany": [

            "germany",
            "german",
            "deutschland",
            "deutsch",

        ],

        "france": [

            "france",
            "french",
            "frankreich",
            "französisch",
            "franzoesisch",

        ],

        "italy": [

            "italy",
            "italian",
            "italien",
            "italienisch",

        ],

        "spain": [

            "spain",
            "spanish",
            "spanien",
            "spanisch",

        ],

        "netherlands": [

            "netherlands",
            "dutch",
            "niederlande",
            "niederländisch",
            "niederlaendisch",

        ],

    }

    aliases = country_aliases.get(
        country,
        [country]
    )

    return any(
        alias in text
        for alias in aliases
    )


# ============================================================
# PRODUCT SIGNAL
# ============================================================

def has_product_signal(
    title: str,
    snippet: str
) -> bool:

    text = (
        (title or "")
        + " "
        + (snippet or "")
    ).lower()

    product_terms = [

        "peanut",
        "peanuts",
        "groundnut",
        "groundnuts",
        "groundnut kernels",
        "peanut kernels",
        "erdnuss",
        "erdnüsse",
        "erdnusskerne",
        "erdnusskern",

    ]

    return any(
        term in text
        for term in product_terms
    )


# ============================================================
# HARD SCORE
# ============================================================

def calculate_hard_score(
    result: dict,
    target_market: str = ""
) -> int:

    title = result.get(
        "title",
        ""
    )

    snippet = result.get(
        "snippet",
        ""
    )

    score = 0

    # Company signal
    if has_company_signal(
        title,
        snippet
    ):
        score += 35

    # Buyer signal
    if has_buyer_signal(
        title,
        snippet
    ):
        score += 30

    # Target country
    if has_target_country_signal(
        title,
        snippet,
        target_market
    ):
        score += 15

    # Product
    if has_product_signal(
        title,
        snippet
    ):
        score += 20

    return score


# ============================================================
# HARD FILTER
# ============================================================

def hard_filter_result(
    result: dict,
    target_market: str = ""
) -> tuple[bool, str]:

    url = result.get(
        "url",
        ""
    )

    title = result.get(
        "title",
        ""
    )

    snippet = result.get(
        "snippet",
        ""
    )


    # --------------------------------------------------------
    # NORMALIZE URL
    # --------------------------------------------------------

    normalized_url = normalize_url(
        url
    )

    if not normalized_url:

        return (
            False,
            "invalid_url"
        )


    # --------------------------------------------------------
    # NORMALIZE DOMAIN
    # --------------------------------------------------------

    domain = normalize_domain(
        normalized_url
    )

    if not domain:

        return (
            False,
            "invalid_domain"
        )


    # --------------------------------------------------------
    # BLACKLISTED DOMAIN
    # --------------------------------------------------------

    if is_blacklisted_domain(
        domain
    ):

        return (
            False,
            "blacklisted_domain"
        )


    # --------------------------------------------------------
    # BAD URL PATTERN
    # --------------------------------------------------------

    if has_bad_url_pattern(
        normalized_url
    ):

        return (
            False,
            "bad_url_pattern"
        )


    # --------------------------------------------------------
    # INFORMATION / ARTICLE
    # --------------------------------------------------------

    if looks_like_information_page(
        title,
        snippet
    ):

        return (
            False,
            "information_page"
        )


    # --------------------------------------------------------
    # LISTING / MARKETPLACE
    # --------------------------------------------------------

    if looks_like_listing_platform(
        title,
        snippet,
        normalized_url
    ):

        return (
            False,
            "listing_platform"
        )


    # --------------------------------------------------------
    # PRODUCT / CATEGORY PAGE
    # --------------------------------------------------------

    if looks_like_product_listing_page(
        normalized_url
    ):

        return (
            False,
            "product_listing_page"
        )


    # --------------------------------------------------------
    # SUPPLIER ONLY
    # --------------------------------------------------------

    if looks_like_supplier_only(
        title,
        snippet
    ):

        return (
            False,
            "supplier_only"
        )


    # --------------------------------------------------------
    # RETAIL
    # --------------------------------------------------------

    if looks_like_retail(
        title,
        snippet,
        normalized_url
    ):

        return (
            False,
            "retail"
        )


    # --------------------------------------------------------
    # SIGNALS
    # --------------------------------------------------------

    company_signal = has_company_signal(
        title,
        snippet
    )

    buyer_signal = has_buyer_signal(
        title,
        snippet
    )

    country_signal = has_target_country_signal(
        title,
        snippet,
        target_market
    )

    product_signal = has_product_signal(
        title,
        snippet
    )


    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    score = calculate_hard_score(

        result,

        target_market

    )


    # --------------------------------------------------------
    # HARD FILTER PHILOSOPHY
    #
    # We are NOT requiring buyer_signal.
    #
    # We only want to eliminate obvious garbage.
    # The AI classifier will make the actual buyer
    # decision later.
    # --------------------------------------------------------

    if score < 30:

        return (
            False,
            "low_quality"
        )


    # --------------------------------------------------------
    # STORE METADATA
    # --------------------------------------------------------

    result["url"] = normalized_url

    result["domain"] = domain

    result["hard_filter_score"] = score

    result["company_signal"] = company_signal

    result["buyer_signal"] = buyer_signal

    result["country_signal"] = country_signal

    result["product_signal"] = product_signal


    return (
        True,
        "candidate"
    )


# ============================================================
# FILTER ALL SERP RESULTS
# ============================================================

def filter_serp_results(
    results: list[dict],
    target_market: str = ""
) -> list[dict]:

    candidates = []

    seen_domains = set()


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


    # ========================================================
    # PROCESS RESULTS
    # ========================================================

    for original_result in results:

        result = dict(
            original_result
        )


        accepted, reason = hard_filter_result(

            result,

            target_market

        )


        if not accepted:

            stats[reason] = (
                stats.get(
                    reason,
                    0
                ) + 1
            )

            continue


        domain = result.get(
            "domain",
            ""
        )


        # ====================================================
        # DOMAIN DEDUPLICATION
        # ====================================================

        if domain in seen_domains:

            stats[
                "duplicates"
            ] += 1

            continue


        seen_domains.add(
            domain
        )


        candidates.append(
            result
        )

        stats[
            "accepted"
        ] += 1


    # ========================================================
    # SORT BY HARD SCORE
    # ========================================================

    candidates.sort(

        key=lambda item:
        item.get(
            "hard_filter_score",
            0
        ),

        reverse=True

    )


    # ========================================================
    # PRINT FILTER STATISTICS
    # ========================================================

    print(
        "\n=============================="
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


    return candidates


# ============================================================
# COMPATIBILITY WRAPPER
# ============================================================

def classify_urls(
    serp_results,
    target_market: str = ""
):

    """
    Compatibility wrapper for the existing pipeline.

    Accepts either:

        list[dict]

    or an object containing:

        .results
    """

    if hasattr(
        serp_results,
        "results"
    ):

        results = (
            serp_results.results
        )

    else:

        results = serp_results


    return filter_serp_results(

        results,

        target_market

    )