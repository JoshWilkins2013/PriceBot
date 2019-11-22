from pricebot.Analyzer import Analyzer
from pricebot.Pages.Craigslist import Craigslist

page = Craigslist()
last_update = page.get_apt_results(zip_code='01923', radius=10, sub_category='nos', max_price=1500, overwrite=True)

az = Analyzer(file_path=".\\Data\\", file_type="Apartment", file_name='Apartments_BostonCraigslist.csv', last_update=last_update)
az.data = az.data[az.data['Area'] < 3000]
az.data = az.data[500 < az.data['Price']]
az.plot_results()
