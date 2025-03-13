import os
import asyncio
import json
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

class Job(BaseModel):
    title: str = Field(description="Job title from the listing")
    company: str = Field(description="Company offering the position")
    location: str = Field(description="Job location in the Philippines")
    salary: str = Field(description="Salary range if available")
    description: str = Field(description="Key responsibilities and requirements")
    link: str = Field(description="URL to full job posting")

async def main():
    # 1. Configure LLM strategy with optimized parameters
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="groq/llama3-8b-8192",
            api_token=os.getenv('GROQ_API_KEY'),
        ),
        schema=Job.model_json_schema(),
        extraction_type="schema",
        instruction="Extract job listings with all fields from the HTML content. Focus on full-time positions in the Philippines.",
        chunk_token_threshold=3500,
        overlap_rate=0.15,
        apply_chunking=True,
        input_format="html",
        extra_args={
            "temperature": 0.1,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"}
        }
    )

    # 2. Configure crawler settings
    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,
        css_selector="div.job-card, .job-listing",  # Target job containers
        wait_until="networkidle",  # ✅ Fixed from "networkidle2"
        page_timeout=120000  # ✅ Increased timeout
    )

    # 3. Browser configuration
    browser_cfg = BrowserConfig(
        headless=True,
        browser_type="chromium",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(
            url="https://ph.jobstreet.com/job-search/job-vacancy.php",
            config=crawl_config
        )

        if result.success:
            try:
                jobs = json.loads(result.extracted_content)
                print(f"✅ Found {len(jobs)} jobs.")
                
                # Save jobs to a text file
                with open("jobs_output.txt", "w", encoding="utf-8") as f:
                    json.dump(jobs, f, indent=4, ensure_ascii=False)
                
                print("📂 Job data saved to 'jobs_output.txt'.")

                print("\nToken Usage:")
                llm_strategy.show_usage()
            except json.JSONDecodeError:
                error_message = "⚠️ JSON parsing failed. Raw output:\n" + result.extracted_content[:2000]
                
                # Save error log
                with open("jobs_error_log.txt", "w", encoding="utf-8") as f:
                    f.write(error_message)
                
                print(error_message)
                print("📂 Error log saved to 'jobs_error_log.txt'.")
        else:
            error_message = f"❌ Crawling failed: {result.error_message}"

            # Save error log
            with open("jobs_error_log.txt", "w", encoding="utf-8") as f:
                f.write(error_message)
            
            print(error_message)
            print("📂 Error log saved to 'jobs_error_log.txt'.")

if __name__ == "__main__":
    asyncio.run(main())
