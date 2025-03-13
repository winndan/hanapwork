import requests
from scrapy import Selector

# Define JobStreet URL
url = "https://ph.jobstreet.com/jobs/"

# Set headers to avoid bot detection
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    selector = Selector(text=response.text)

    # Extract all job postings
    job_articles = selector.css("article")

    if job_articles:
        print(f"\nExtracted {len(job_articles)} job postings:\n")

        for index, job_article in enumerate(job_articles[:10]):  # Limit to 10 for testing
            job_selector = Selector(text=job_article.get())

            # Extract Job Title
            job_title = job_selector.css('[data-automation="jobTitle"]::text').get() or "Not found"

            # Extract Job Link
            job_link = job_selector.css('[data-automation="jobTitle"]::attr(href)').get()
            if job_link:
                job_link = "https://ph.jobstreet.com" + job_link  # Append domain if needed
            else:
                job_link = "Not found"

            # Extract Company Name
            company_name = job_selector.css('a[data-automation="jobCompany"]::text').get()
            if not company_name:
                company_name = job_selector.css('div[class*="company"] span::text').get()
            if not company_name:
                company_name = "Not found"

            # Extract Job Location
            job_location = job_selector.css('[data-automation="jobLocation"]::text').get() or "Not found"

            # Extract Salary from Job Detail Page
            job_salary = "Not listed"
            if job_link != "Not found":
                detail_response = requests.get(job_link, headers=headers)
                if detail_response.status_code == 200:
                    detail_selector = Selector(text=detail_response.text)
                    job_salary = detail_selector.css('[data-automation="job-detail-salary"]::text').get()
                    if not job_salary:
                        job_salary = "Not listed"

            # Extract Job Description
            job_desc = job_selector.css("div._1q03wcw4::text, p::text").get() or "Description not available."

            print(f"📝 Job {index+1}:")
            print(f"   🔹 Company: {company_name}")
            print(f"   📌 Job Title: {job_title}")
            print(f"   🌐 Link: {job_link}")
            print(f"   📍 Location: {job_location}")
            print(f"   💰 Salary: {job_salary} ✅" if job_salary != "Not listed" else "   ⚠️ Salary: Not listed ❌")
            print(f"   📄 Description: {job_desc[:150]}...")
            print("-" * 50)

    else:
        print("No job postings found.")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
