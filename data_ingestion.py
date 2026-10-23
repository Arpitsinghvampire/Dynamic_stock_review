
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO
import json

load_dotenv()

search_tools = TavilySearch(
    max_results=10,
    topic="general"
)


def get_docs(company_name: str):
    docs = []

    queries = [
        # Official financial information
        f'"{company_name}" official annual report financial results',
        f'"{company_name}" quarterly results revenue net profit FY 2025-26',

        # Financial health
        f'"{company_name}" total debt net debt interest expense latest results',
        f'"{company_name}" cash flow debt repayment credit rating',

        # Business operations
        f'"{company_name}" new projects capital expenditure expansion',
        f'"{company_name}" acquisitions mergers divestments',

        # Legal and regulatory risks
        f'"{company_name}" court cases litigation regulatory investigation',
        f'"{company_name}" SEBI notices environmental violations penalties',

        # Recent developments
        f'"{company_name}" latest business news October 2026',
        f'"{company_name}" risks outlook analyst report',
    ]

    for query in queries:
        try:
            responses = search_tools.invoke({"query": query})

            # Normalize the response if this version returns JSON text
            if isinstance(responses, str):
                try:
                    responses = json.loads(responses)
                except json.JSONDecodeError:
                    print(f"Unexpected Tavily response for: {query}")
                    print(responses[:300])
                    continue

            # Support a list of results or a dictionary containing results
            if isinstance(responses, list):
                results = responses
            elif isinstance(responses, dict):
                results = responses.get("results", [])
            else:
                print(f"Unexpected response type: {type(responses)}")
                continue

            for result in results:
                if not isinstance(result, dict):
                    continue

                docs.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("content", "")
                })

        except Exception as error:
            print(f"Search failed for '{query}': {error}")
            continue

    # Remove duplicate URLs
    unique_results = {}

    for item in docs:
        url = item["url"].strip()

        if url:
            unique_results[url] = item

    return list(unique_results.values())


def extract_page_text(unique_results):
    final_text_doc = []

    for result in unique_results:
        url = result.get("url", "")

        if not url:
            continue

        try:
            response = requests.get(
                url,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            # Detect PDF using its header, MIME type, or URL
            is_pdf = (
                "application/pdf" in content_type
                or response.content.startswith(b"%PDF-")
                or url.lower().split("?")[0].endswith(".pdf")
            )

            if is_pdf:
                reader = PdfReader(BytesIO(response.content))

                page_texts = []

                for page in reader.pages:
                    text = page.extract_text() or ""

                    if text.strip():
                        page_texts.append(text)

                page_text = "\n".join(page_texts)

            else:
                # Parse normal HTML
                soup = BeautifulSoup(
                    response.content,
                    "html.parser"
                )

                for tag in soup([
                    "script", "style", "nav",
                    "footer", "header", "noscript"
                ]):
                    tag.decompose()

                page_text = soup.get_text(
                    separator=" ",
                    strip=True
                )

            # Skip empty or unusable pages
            if len(page_text.strip()) < 200:
                print(f"Insufficient text extracted: {url}")
                continue

            # Preserve metadata alongside the text
            final_text_doc.append({
                "title": result.get("title", ""),
                "url": url,
                "text": page_text
            })

        except Exception as error:
            print(f"Could not process {url}: {error}")
            continue

    return final_text_doc


if __name__ == "__main__":
    company_name = "Vedanta"
    search_results = get_docs(company_name)
    extracted_docs = extract_page_text(search_results)

    print(f"Search results: {len(search_results)}")
    print(f"Successfully extracted: {len(extracted_docs)}")

    for doc in extracted_docs:
        print("\nTitle:", doc["title"])
        print("URL:", doc["url"])
        print("Extracted text:", doc["text"][:500])

