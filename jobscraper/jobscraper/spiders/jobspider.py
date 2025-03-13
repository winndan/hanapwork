import scrapy
from scrapy.selector import Selector

class JobspiderSpider(scrapy.Spider):
    name = "jobspider"
    allowed_domains = ["ph.jobstreet.com"]
    start_urls = ["https://ph.jobstreet.com/jobs/"]
    
    page_count = 0  # Counter to track the number of pages crawled
    max_pages = 10  # Limit to 10 pages

    def parse(self, response):
        # Extract all job postings
        job_articles = response.css("article")

        if job_articles:
            self.logger.info(f"Extracted {len(job_articles)} job postings.")

            for job_article in job_articles[:10]:  # Limit to 10 for testing
                job_selector = Selector(text=job_article.get())

                # Extract Job Title
                job_title = job_selector.css('[data-automation="jobTitle"]::text').get(default="Not found")

                # Extract Job Link
                job_link = job_selector.css('[data-automation="jobTitle"]::attr(href)').get()
                if job_link:
                    job_link = response.urljoin(job_link)  # Convert relative URL to absolute
                else:
                    job_link = "Not found"

                # Extract Company Name
                company_name = job_selector.css('a[data-automation="jobCompany"]::text').get()
                if not company_name:
                    company_name = job_selector.css('div[class*="company"] span::text').get(default="Not found")

                # Extract Job Location
                job_location = job_selector.css('[data-automation="jobLocation"]::text').get(default="Not found")

                # Extract Job Description
                job_desc = job_selector.css("div._1q03wcw4::text, p::text").get(default="Description not available.")

                # Log extracted data for debugging
                self.logger.info(f"Extracted job: {job_title} at {company_name}, Location: {job_location}")
                print(f"Extracted job: {job_title} at {company_name}, Location: {job_location}")

                # Yield job details
                yield scrapy.Request(
                    job_link,
                    callback=self.parse_job_details,
                    meta={
                        'job_title': job_title,
                        'job_link': job_link,
                        'company_name': company_name,
                        'job_location': job_location,
                        'job_desc': job_desc
                    },
                    errback=self.handle_error
                )

        # Extract and follow the next page if the limit is not reached
        if self.page_count < self.max_pages:
            next_page = response.css('a[aria-label="Next"]::attr(href)').get()
            if next_page:
                next_page_url = response.urljoin(next_page)
                self.page_count += 1
                self.logger.info(f"Following next page: {next_page_url} (Page {self.page_count})")
                yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_job_details(self, response):
        job_salary = response.css('[data-automation="job-detail-salary"]::text').get(default="Not listed")
        
        job_data = {
            'job_title': response.meta['job_title'],
            'job_link': response.meta['job_link'],
            'company_name': response.meta['company_name'],
            'job_location': response.meta['job_location'],
            'job_salary': job_salary,
            'job_desc': response.meta['job_desc']
        }
        
        self.logger.info(f"Final extracted job details: {job_data}")
        print(f"Final extracted job details: {job_data}")

        yield job_data

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure.request.url}")
        print(f"Request failed: {failure.request.url}")
