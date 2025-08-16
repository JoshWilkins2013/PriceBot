import os

from pricebot.Pages.Page import Page
from pricebot.Ads.FacebookAd import CarAd


class Facebook(Page):
    def get_car_results(self, make=None, model=None, radius=50):
        make = input("Make: ").capitalize() if not make else make
        model = input("Model: ").capitalize() if not model else model
        radius = input("Radius: ") if not radius else radius

        fname = f"{make}{model}_{self.site}Facebook.csv"
        data_path = os.path.join("Data", fname)

        # Build URL
        url = f"https://www.facebook.com/marketplace/105575119474848/search?deliveryMethod=local_pick_up&query={make}%20{model}&exact=false&minPrice=500"
        ad_class = "x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x135b78x x11lfxj5 x1iorvi4 xjkvuk6 xnpuxes x1cjf5ee x17dddeq"

        for ad in self.get_ads(url, ad_class):
            car_ad = CarAd(ad)
            car_ad.get_link()
            car_ad.get_price()
            car_ad.get_year()
            car_ad.get_meta_data()
            self.ads.append(car_ad)

        if len(self.ads) == 0:
            print(f"No new ads found for {make} {model} at {self.site}. Not writing CSV.")
            return

        self.save_ads(data_path)
