from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# Common elements that are usually irrelevant
REMOVE_SELECTORS = [
    "script",
    "style",
    "noscript",
    "svg",
    "iframe",

    # Navigation / footer
    "nav",
    "footer",
    "header",

    # Cookie / consent
    "[id*='cookie']",
    "[class*='cookie']",
    "[id*='consent']",
    "[class*='consent']",
    "[id*='privacy']",
    "[class*='privacy']",

    # Common popup/modal elements
    "[role='dialog']",
    "[role='alertdialog']",

    # Common German consent elements
    "[id*='datenschutz']",
    "[class*='datenschutz']",
]


def clean_text(text):

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        line = " ".join(line.split())

        if len(line) < 3:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def scrape_website(url):

    scraped_data = {
        "url": url,
        "title": None,
        "text_content": "",
        "links": []
    }

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 900
            }
        )

        try:

            print(f"\nScraping: {url}")

            page.goto(
                url,
                timeout=30000,
                wait_until="domcontentloaded"
            )

            # Allow JavaScript content to load
            page.wait_for_timeout(3000)

            scraped_data["title"] = page.title()

            # ------------------------------------------------
            # REMOVE COOKIE / POPUP / NAVIGATION ELEMENTS
            # BEFORE GETTING HTML
            # ------------------------------------------------

            for selector in REMOVE_SELECTORS:

                try:

                    elements = page.locator(
                        selector
                    )

                    count = elements.count()

                    for i in range(count):

                        try:
                            elements.nth(i).evaluate(
                                "(element) => element.remove()"
                            )
                        except:
                            pass

                except:
                    pass


            # ------------------------------------------------
            # GET CLEAN HTML
            # ------------------------------------------------

            html = page.content()


            soup = BeautifulSoup(
                html,
                "lxml"
            )


            # ------------------------------------------------
            # SECOND CLEANUP USING BEAUTIFULSOUP
            # ------------------------------------------------

            for selector in REMOVE_SELECTORS:

                try:

                    for element in soup.select(
                        selector
                    ):

                        element.decompose()

                except:
                    pass


            # ------------------------------------------------
            # TRY TO FIND MAIN CONTENT
            # ------------------------------------------------

            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find("body")
            )


            if main_content:

                raw_text = main_content.get_text(
                    separator="\n",
                    strip=True
                )

            else:

                raw_text = soup.get_text(
                    separator="\n",
                    strip=True
                )


            # ------------------------------------------------
            # CLEAN TEXT
            # ------------------------------------------------

            clean_content = clean_text(
                raw_text
            )


            scraped_data[
                "text_content"
            ] = clean_content


            # ------------------------------------------------
            # EXTRACT LINKS
            # ------------------------------------------------

            links = []

            for a in soup.find_all("a"):

                href = a.get("href")

                if not href:
                    continue

                absolute_url = urljoin(
                    url,
                    href
                )

                if absolute_url not in links:

                    links.append(
                        absolute_url
                    )


            scraped_data[
                "links"
            ] = links


        except Exception as e:

            print(
                f"Error scraping {url}: {e}"
            )


        finally:

            browser.close()


    return scraped_data