import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Apartments(object):
    def __init__(self, site="Boston"):
        self.site = site

    def get_apt_results(self, city, state, max_price=4000, overwrite=False, min_price=0):
            fname = f"Apartments_{self.site}Craigslist.csv"
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

            html = driver.page_source
            driver.quit()

            soup = BeautifulSoup(html, 'html.parser')
            # Craigslist apartment listings are in li with class 'result-row'
            ads = soup.find_all('div', {'class': 'cl-search-result cl-search-view-mode-gallery'})

            if not ads:
                print("No apartment listings found or page structure changed.")

            ads_info = []

            for ad in ads:
                ad_info = {}

                # Title and link
                title_tag = ad.find('a', class_='cl-app-anchor cl-search-anchor text-only posting-title')
                ad_info['Title'] = title_tag.text.strip() if title_tag else ''
                ad_info['Link'] = title_tag['href'] if title_tag else ''

                # Price
                price_tag = ad.find('span', class_='priceinfo')
                ad_info['Price'] = price_tag.text.strip().lstrip('$') if price_tag else ''

                # Date posted
                date_tag = ad.find('time', class_='result-date')
                ad_info['Date'] = date_tag['datetime'] if date_tag and date_tag.has_attr('datetime') else ''

                # Housing info
                housing_info = ad.find('span', class_='housing-meta')
                if housing_info:
                    housing_text = housing_info.text.strip()
                    # Try to extract bedrooms and size from housing text
                    br = housing_info.find('span', class_='post-bedrooms')
                    size = housing_info.find('span', class_="post-sqft")


                    ad_info['Bedrooms'] = br.text.strip() if br else ''
                    ad_info['Size'] = size.text.strip() if size else ''
                else:
                    ad_info['Bedrooms'] = ''
                    ad_info['Size'] = ''

                # # Location (neighborhood)
                # hood = ad.find('span', class_='result-hood')
                # ad_info['Location'] = hood.text.strip(" ()") if hood else ''

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
