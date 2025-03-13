# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import testss


class JobscraperItem(testss.Item):
    title = testss.Field()  # Job title
    company = testss.Field()  # Company name
    location = testss.Field()  # Job location
    salary = testss.Field()  # Salary (if available)
    description = testss.Field()  # Job description
    url = testss.Field()  # Job listing URL
