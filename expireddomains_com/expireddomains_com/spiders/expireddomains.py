import scrapy
import pandas as pd
from selenium.webdriver import Chrome, ChromeOptions
from time import sleep
import os
import csv


class ExpireddomainsComSpiderSpider(scrapy.Spider):
    name = 'expireddomains_com_spider'
    custom_settings = {
        'FEED_URI': f"output/{name.replace('_spider','_data')}.csv",
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'ROBOTSTXT_OBEY': True
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        csv_path = r"E:\Godaddy\expireddomains_com\expireddomains_com\spiders\domain.csv"

   
        self.domains = pd.read_csv(csv_path)['Domain'].tolist()
        self.output_file = "output_data1.csv"
        with open(self.output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["domain", "GoValueUSD", "DomainName"])
            writer.writeheader()  

    def start_requests(self):
        for domain in self.domains:
            self.process_with_selenium(domain)

    def process_with_selenium(self, domain):
        options = ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--headless')  
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        )

        driver = Chrome(options=options)

        try:
            url = f"https://ph.godaddy.com/domainfind/v1/search/exact?key=appraisals_search&q={domain}"
            driver.get(url)
            sleep(3)  

            page_source = driver.page_source

            go_value_usd = None
            domain_name = None

            if '"GoValueUSD":' in page_source:
                start = page_source.index('"GoValueUSD":') + len('"GoValueUSD":')
                go_value_usd = page_source[start:].split(',')[0].strip()

            if '"DomainName":' in page_source:
                start = page_source.index('"GoValueUSD":') + len('"GoValueUSD":')
                domain_name = page_source[start:].split(',')[0].strip().replace('"', '')

            result = ({
                'domain': domain,
                'GoValueUSD': go_value_usd,
                
            })
            
            with open(self.output_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=["domain", "GoValueUSD", "DomainName"])
                writer.writerow(result)

        except Exception as e:
            self.logger.error(f"Error processing {domain}: {e}")

        finally:
            driver.quit()
