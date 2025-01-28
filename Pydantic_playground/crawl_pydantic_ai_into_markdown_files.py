import os
import asyncio
import requests
from xml.etree import ElementTree
from urllib.parse import urlparse
from dotenv import load_dotenv

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

load_dotenv()

def save_markdown_file(url: str, markdown: str, output_dir: str = "pydantic_docs"):
    """Save markdown content to a file based on URL structure."""
    os.makedirs(output_dir, exist_ok=True)

    parsed = urlparse(url)
    path = parsed.path.strip('/')
    filename = "index.md" if not path else f"{path.replace('/', '_')}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Source URL: {url}\n\n{markdown}")
    print(f"Saved: {filepath}")

def aggregate_markdown_files(urls: list, input_dir: str = "pydantic_docs", output_file: str = "aggregated_docs.md"):
    """Combine all markdown files into one, preserving URL order."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for url in urls:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            filename = "index.md" if not path else f"{path.replace('/', '_')}.md"
            filepath = os.path.join(input_dir, filename)

            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read() + "\n\n")

async def crawl_parallel(urls: list, max_concurrent: int = 5):
    """Crawl URLs with concurrency control."""
    crawler = AsyncWebCrawler(config=BrowserConfig(
        headless=True,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
    ))
    await crawler.start()

    try:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_url(url: str):
            async with semaphore:
                result = await crawler.arun(
                    url=url,
                    config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS),
                    session_id="session1"
                )
                if result.success:
                    save_markdown_file(url, result.markdown_v2.raw_markdown)
                else:
                    print(f"Failed: {url} - {result.error_message}")

        await asyncio.gather(*(process_url(url) for url in urls))
    finally:
        await crawler.close()

def get_pydantic_ai_docs_urls() -> list:
    """Extract URLs from sitemap.xml."""
    sitemap = requests.get("https://ai.pydantic.dev/sitemap.xml").content
    return [loc.text for loc in ElementTree.fromstring(sitemap).findall('.//{*}loc')]

async def main():
    urls = get_pydantic_ai_docs_urls()
    if not urls:
        print("No URLs found")
        return

    print(f"Crawling {len(urls)} URLs...")
    await crawl_parallel(urls)

    print("Aggregating markdown files...")
    aggregate_markdown_files(urls)

if __name__ == "__main__":
    asyncio.run(main())
