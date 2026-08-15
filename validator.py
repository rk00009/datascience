ALLOWED_SOURCES=[
"google_search",
"trade_directories",
"company_websites",
"trade_show_exhibitors"
]


def validate_sources(sources):

    for source in sources:

        if source not in ALLOWED_SOURCES:
            return False

    return True