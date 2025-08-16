import os

from pricebot.Pages.Page import Page
from pricebot.Ads.CraigslistAd import CarAd
from pricebot.Ads.CraigslistAd import AptAd


class Craigslist(Page):
    def get_car_results(self, make=None, model=None, radius=50):
        make = input("Make: ").capitalize() if not make else make
        model = input("Model: ").capitalize() if not model else model
        radius = input("Radius: ") if not radius else radius

        fname = f"{make}{model}_{self.site}Craigslist.csv"
        data_path = os.path.join("Data", fname)

        # Build URL
        url = f"https://{self.site.lower()}.craigslist.org/search/cta?query={make}+{model}&search_distance={radius}&min_price=500"
        ad_class = 'cl-search-result cl-search-view-mode-gallery'

        for ad in self.get_ads(url, ad_class):
            car_ad = CarAd(ad)
            car_ad.get_title_info()
            car_ad.get_price()
            car_ad.get_meta_data()
            car_ad.get_date()
            self.ads.append(car_ad)

        if len(self.ads) == 0:
            print(f"No new ads found for {make} {model} at {self.site}. Not writing CSV.")
            return

        self.save_ads(data_path)

    #########################################################

    def get_apt_results(self, radius=20, max_price=1600, min_price=0):
            fname = f"Apartments_{self.site}Craigslist.csv"
            data_path = os.path.join("Data", fname)

            # Build the Craigslist URL for apartments
            url = (f"https://{self.site.lower()}.craigslist.org/search/apa?"
                f"search_distance={radius}&max_price={max_price}&min_price={min_price}")

            for ad in self.get_ads(url):
                apt_ad = AptAd(ad)
                apt_ad.get_title_info()
                apt_ad.get_meta_data()
                apt_ad.get_price()
                self.ads.append(apt_ad)

            if len(self.ads) == 0:
                print(f"No new ads found {self.site}. Not writing CSV.")
                return

            self.save_ads(data_path)
