import os
import time
import pickle
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Page:
    def __init__(self, site, use_cookies=True):
        self.ads = []
        self.site = site
        self.use_cookies = use_cookies
        self.cookies_file = f"{site}_cookies.pkl"

    def _load_cookies(self, driver):
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, "rb") as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
            print(f"Loaded {len(cookies)} cookies from {self.cookies_file}")
            driver.refresh()

    def _save_cookies(self, driver):
        with open(self.cookies_file, "wb") as f:
            pickle.dump(driver.get_cookies(), f)
        print(f"Saved {len(driver.get_cookies())} cookies to {self.cookies_file}")

    def get_ads(self, url, ad_class, scroll_time=10, refresh=True):
        """Load page, apply cookies, optionally scroll and scrape ads"""
        print(f"Loading URL: {url}")

        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)

        # Load cookies if enabled
        if self.use_cookies and os.path.exists(self.cookies_file):
            self._load_cookies(driver)
            if refresh:
                driver.refresh()
                time.sleep(3)

        # Scroll for content
        if scroll_time > 0:
            start_time = time.time()
            last_height = driver.execute_script("return document.body.scrollHeight")
            while time.time() - start_time < scroll_time:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

        html = driver.page_source

        # Save cookies after scraping
        if self.use_cookies:
            self._save_cookies(driver)

        driver.quit()

        # Parse ads
        soup = BeautifulSoup(html, 'html.parser')
        ads = soup.find_all('div', {'class': ad_class})
        if not ads:
            raise Exception("No listings found or page structure changed.")

        return ads

    def save_ads(self, data_path):
        data_dir = os.path.dirname(data_path)
        os.makedirs(data_dir, exist_ok=True)

        # Save dataframe to csv
        all_data = pd.concat([ad.to_series() for ad in self.ads], axis=1).T
        all_data.to_csv(data_path, index=False)

        print(f"Wrote {len(all_data)} records to new file {data_path}")