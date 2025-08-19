from pricebot.Analyzer import Analyzer
from pricebot.Pages.Craigslist import Craigslist
from pricebot.Pages.Facebook import Facebook
from pricebot.Pages.Apartments import Apartments

site = "Facebook"
city = "Rochester"

# apartmentsPage = Apartments

# Apartments(city).get_apt_results(city, "ny")

page = Craigslist(city) if site == "Craigslist" else Facebook(city, use_cookies=True)

page.get_apt_results(zip_code='14467', radius=10, sub_category='nos', max_price=2000, overwrite=True, min_price=900)

# az = Analyzer(file_path=".\\Data\\", file_type="Apartment", file_name='Apartments.csv')
# az.data = az.data[az.data['Area'] < 3000]
# az.data = az.data[500 < az.data['Price']]
# az.plot_results()
