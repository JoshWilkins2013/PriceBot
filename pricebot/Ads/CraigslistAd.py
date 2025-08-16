import re

from pricebot.Ads.Ad import Ad


class CraigslistAd(Ad):
    def __init__(self, ad):
        super().__init__(ad)
        self.date = None

        self.title_tag = self.ad.find('a', class_='cl-app-anchor cl-search-anchor text-only posting-title')
        self.meta_tag = self.ad.find('div', class_='meta')

    def get_title_info(self):
        if self.title_tag is not None:
            label_span = self.title_tag.find('span', class_='label')
            self.title = label_span.text.strip() if label_span else self.title
            self.link = self.title_tag['href']

    def get_price(self):
        price_tag = self.ad.find('span', class_='priceinfo')
        if price_tag is not None:
            self.price = price_tag.text.strip().lstrip('$')

    def get_date(self):
        date_tag = self.ad.find('time', class_='result-date')
        self.date = date_tag['datetime'] if date_tag and date_tag.has_attr('datetime') else self.date


class CarAd(CraigslistAd):
    def __init__(self, ad):
        super().__init__(ad)

        self.year = None
        self.mileage = None
        self.town = None

    def get_title_info(self):
        if self.title_tag is not None:
            super().get_title_info()  # Title, link
            if year_in_title := re.search("[1|2][0|1|2|9][0-9]{2}", self.title_tag.text):
                self.year = year_in_title.group(0)

    def get_meta_data(self):
        if self.meta_tag:
            date_text = self.meta_tag.contents[0].strip() if self.meta_tag.contents else ''
            self.date = date_text

            meta_texts = []
            for elem in self.meta_tag.children:
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

            mileage = meta_texts[0] if len(meta_texts) > 0 else None
            self.mileage = re.search("[0-9]+", mileage).group(0)
            self.town = meta_texts[1] if len(meta_texts) > 1 else None


class AptAd(CraigslistAd):
    def __init__(self, ad):
        super().__init__(ad)

        self.area = None
        self.bedrooms = None

    def get_meta_data(self):
        if self.meta_tag is not None:
            # Try to extract bedrooms and area size from housing text
            br = self.meta_tag.find('span', class_='post-bedrooms')
            area = self.meta_tag.find('span', class_="post-sqft")

            self.area = area.text.strip() if area else self.area
            self.bedrooms = br.text.strip() if br else self.bedrooms
