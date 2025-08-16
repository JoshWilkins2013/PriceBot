import os
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Page:
    def __init__(self, site):
        self.ads = []
        self.site = site

    @staticmethod
    def get_ads(url, ad_class):
        print(f"Loading URL: {url}")

        driver = webdriver.Chrome(options=Options())
        driver.get(url)
        time.sleep(4)  # Todo: replace with element search

        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')
        ads = soup.find_all('div', {'class': ad_class})

        if not ads:
            raise "No listings found or page structure changed."

        return ads

    def save_ads(self, data_path):
        data_dir = os.path.dirname(data_path)
        os.makedirs(data_dir, exist_ok=True)

        # Save dataframe to csv
        all_data = pd.concat([ad.to_series() for ad in self.ads], axis=1).T
        all_data.to_csv(data_path, index=False)

        print(f"Wrote {len(all_data)} records to new file {data_path}")