import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pickle

class Apartments(object):
    def __init__(self, site="Boston", use_cookies=False):
        self.site = site
        self.use_cookies = use_cookies
        self.cookies_file = f"{site}_cookies.pkl"

    def _load_cookies(self, driver):
        "Load cookies into selenium"
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, "rb") as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
            print(f"Loaded {len(cookies)}")

    def _save_cookies(self, driver):
        "Save cookies from selenium session"
        cookies = driver.get_cookies()
        with open(self.cookies_file, "wb") as f:
            pickle.dump(cookies, f)
        print(f"Saved {len(cookies)}")

    def get_apt_results(self, city, state, max_price=4000, overwrite=False, min_price=0):
            fname = f"Apartments_{self.site}.csv"
            data_path = os.path.join("Data", fname)

            # Load last update time if file exists and not overwriting
            if os.path.isfile(data_path) and not overwrite:
                try:
                    df = pd.read_csv(data_path, usecols=['Date'])
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                except Exception as e:
                    print(f"Warning: Could not read existing CSV")

            # Build the Craigslist URL for apartments
            url = (f"https://apartments.com/{city}-{state}")

            print(f"Loading URL: {url}")

            options = Options()
            options.headless = True
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(4)

            if self.use_cookies:
                self._load_cookies(driver)
                driver.refresh()

            html = driver.page_source
            driver.quit()

            soup = BeautifulSoup(html, 'html.parser')
            ads = soup.find_all('li', {'class': 'mortar-wrapper'})

            if not ads:
                print("No apartment listings found or page structure changed.")

            ads_info = []

            for ad in ads:
                ad_info = {}

                # Title and link
                title_tag = ad.find('a', class_='property-link')
                ad_info['Title'] = title_tag['aria-label'] if title_tag else ''
                ad_info['Link'] = title_tag['href'] if title_tag else ''

                # Price
                price_tag = ad.find('p', class_='property-pricing')
                ad_info['Price'] = price_tag.text.strip().lstrip('$') if price_tag else ''

                ads_info.append(ad_info)

            if len(ads_info) == 0:
                print(f"No new ads found {self.site}. Not writing CSV.")

            data_dir = os.path.dirname(data_path)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            # Save or append CSV
            if os.path.isfile(data_path) and not overwrite:
                try:
                    existing_df = pd.read_csv(data_path)
                    new_df = pd.DataFrame(ads_info)
                    combined = pd.concat([existing_df, new_df], ignore_index=True)
                    combined.to_csv(data_path, index=False)
                    print(f"Appended {len(new_df)} new records to {data_path}")
                except Exception as e:
                    print(f"Error appending to existing CSV: {e}")
            else:
                pd.DataFrame(ads_info).to_csv(data_path, index=False)
                print(f"Wrote {len(ads_info)} records to new file {data_path}")

            if self.use_cookies:
                driver - webdriver.Chrome(options=options)
                driver.get(url)
                time.sleep(2)
                self._save_cookies(driver)
                driver.quit()
