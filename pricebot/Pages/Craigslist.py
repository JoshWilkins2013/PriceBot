import os
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Craigslist(object):
    def __init__(self, site="Boston"):
        self.site = site

    def get_car_results(self, make=None, model=None, zip_code='01923', radius=50, overwrite=True):
        if not make:
            make = input("Make: ").capitalize()
        if not model:
            model = input("Model: ").capitalize()
        if not zip_code:
            zip_code = input("Zip: ")
        if not radius:
            radius = input("Radius: ")

        fname = f"{make}{model}_{self.site}Craigslist.csv"
        data_path = os.path.join("Data", fname)

        # Load existing data to get last update time
        if os.path.isfile(data_path):
            try:
                df = pd.read_csv(data_path, usecols=['Date'])
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            except Exception as e:
                print(f"Warning: Could not read existing CSV")

        # Build URL
        url = (f"https://{self.site.lower()}.craigslist.org/search/cta?"
               f"query={make}+{model}&search_distance={radius}&postal={zip_code}&min_price=500")

        print(f"Loading URL: {url}")

        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(4)  # Increase if listings still missing

        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')
        ads = soup.find_all('div', {'class': 'cl-search-result cl-search-view-mode-gallery'})

        if not ads:
            print("No listings found or page structure changed.")

        ads_info = []
        
        for ad in ads:
            ad_info = {}
            
            title_tag = ad.find('a', class_='cl-app-anchor cl-search-anchor text-only posting-title')
            
            if title_tag:
                label_span = title_tag.find('span', class_='label')
                ad_info['Title'] = label_span.text.strip() if label_span else ''
                ad_info['Link'] = title_tag['href']
            else:
                ad_info['Title'] = ''
                ad_info['Link'] = ''

            #price
            price_tag = ad.find('span', class_= 'priceinfo')
            ad_info['Price'] = price_tag.text.strip().lstrip('$') if price_tag else ''

            #meta
            meta_tag = ad.find('div', class_='meta')
            
            if meta_tag:
                date_text = meta_tag.contents[0].strip() if meta_tag.contents else ''
                ad_info['Date'] = date_text
              
                meta_texts = []           
                for elem in meta_tag.children:
                    if getattr(elem, 'name', None) == 'span' and 'seperator' in elem.get('class', []):
                        continue
                    if isinstance(elem, str):
                        text = elem.strip()
                        if text and text != date_text:
                            meta_texts.append(text)
                    elif elem.name == 'span':
                        text = elem.get_text(strip=True)
                        if text:
                            meta_texts.append(text)

                ad_info['Mileage'] = meta_texts[0] if len(meta_texts) > 0 else ''
                ad_info['Mileage'] = re.search("[0-9]+", ad_info['Mileage']).group(0)
                ad_info['Town'] = meta_texts[1] if len(meta_texts) > 1 else ''
            else:
                ad_info['Date'] = ''
                ad_info['Mileage'] = ''
                ad_info['Town'] = ''

            #title
            title_tag = ad.find('a', class_='cl-app-anchor cl-search-anchor text-only posting-title')

            if title_tag:
                try:
                    ad_info['Year'] = re.search("[1|2][0|1|2|9][0-9]{2}", title_tag.text).group(0)
                except Exception:
                    ad_info['Year'] = None

            ads_info.append(ad_info)

            if len(ads_info) == 0:
                print(f"No new ads found for {make} {model} at {self.site}. Not writing CSV.")

        data_dir = os.path.dirname(data_path)
        os.makedirs(data_dir, exist_ok=True)

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

    #########################################################

    def get_apt_results(self, zip_code='01923', radius=20, max_price=1600, sub_category=None, overwrite=False, min_price=0):
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
            url = (f"https://{self.site.lower()}.craigslist.org/search/apa?"
                f"search_distance={radius}&postal={zip_code}&max_price={max_price}&min_price={min_price}")

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
                    # Try to extract bedrooms and area size from housing text
                    br = housing_info.find('span', class_='post-bedrooms')
                    area = housing_info.find('span', class_="post-sqft")

                    ad_info['Bedrooms'] = br.text.strip() if br else ''
                    ad_info['Area'] = area.text.strip() if area else ''
                else:
                    ad_info['Bedrooms'] = ''
                    ad_info['Area'] = ''

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
