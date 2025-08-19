import os
from pricebot.Pages.Page import Page
from pricebot.Ads.FacebookAd import CarAd
from pricebot.Ads.FacebookAd import AptAd

class Facebook(Page):

    def __init__(self, city, use_cookies=False):
        super().__init__("Facebook", use_cookies=use_cookies)
        self.city = city

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

    def get_apt_results(self, zip_code='14467', radius=10, sub_category='nos', max_price=2000, overwrite=True, min_price=900):
        zip_code = input("Zip: ").capitalize() if not zip_code else zip_code
        radius = input("Radius: ").capitalize() if not radius else radius
        max_price = input("Max_price: ") if not max_price else max_price

        fname = f"Apartments.csv"
        data_path = os.path.join("Data", fname)

        # Build URL
        url = f"https://www.facebook.com/marketplace/100246126684312/propertyrentals/?maxPrice={max_price}&minPrice={min_price}&minBedrooms=1&exact=true&maxBedrooms=1&minAreaSize=700"
        ad_class = "x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x135b78x x11lfxj5 x1iorvi4 xjkvuk6 xnpuxes x1cjf5ee x17dddeq"

        for ad in self.get_ads(url, ad_class):
            apt_ad = AptAd(ad)
            apt_ad.get_link()
            apt_ad.get_price()
            apt_ad.get_town()
            self.ads.append(apt_ad)

        if len(self.ads) == 0:
            print(f"No new ads found for {zip_code} Not writing CSV.")
            return

        self.save_ads(data_path)
