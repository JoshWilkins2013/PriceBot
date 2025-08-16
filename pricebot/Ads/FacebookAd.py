import re

from pricebot.Ads.Ad import Ad


class FacebookAd(Ad):
    def get_link(self):
        link_tag = self.ad.find('a', class_='x1i10hfl xjbqb8w x1ejq31n x18oe1m7 x1sy0etr xstzfhl x972fbf x10w94by x1qhh985 x14e42zd x9f619 x1ypdohk xt0psk2 x3ct3a4 xdj266r x14z9mp xat24cr x1lziwak xexx8yu xyri2b x18d9i69 x1c1uobl x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xkrqix3 x1sur9pj x1s688f x1lku1pv')
        if link_tag is not None:
            self.link = f"https://facebook.com{link_tag['href']}"

    def get_price(self):
        price_tag = self.ad.find('span', class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u')
        if price_tag is not None:
            self.price = price_tag.text.strip().lstrip('$')


class CarAd(FacebookAd):
    def __init__(self, ad):
        super().__init__(ad)

        self.year = None
        self.mileage = None
        self.town = None

    def get_year(self):
        title_tag = self.ad.find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6')
        if title_tag is not None:
            self.title = title_tag.text
            if year_in_title := re.search("[1|2][0|1|2|9][0-9]{2}", title_tag.text):
                self.year = year_in_title.group(0)

    def get_meta_data(self):
        meta_tags = self.ad.find_all('span', class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84")
        if len(meta_tags) != 0:
            self.town = meta_tags[0].text
        if len(meta_tags) > 1:
            try:
                self.mileage = re.search("[0-9]+", meta_tags[1].text).group(0)
            except AttributeError:
                pass
