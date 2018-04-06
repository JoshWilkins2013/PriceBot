from pricebot.Analyzer import Analyzer
from pricebot.Pages.AutoTempest import AutoTempest
from pricebot.Pages.Craigslist import Craigslist
from pricebot.Pages.Ebay import Ebay

page = AutoTempest()
page.get_car_results()

page = Craigslist()
page.get_car_results()

page = Ebay()
page.get_car_results()

analyzer = Analyzer()
analyzer.plot_results(analyzer.items[0])