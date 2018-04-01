from lib.Analyzer import Analyzer
from lib.Pages.AutoTempest import AutoTempest
from lib.Pages.Craigslist import Craigslist
from lib.Pages.Ebay import Ebay

page = AutoTempest()
page.get_car_results()

page = Craigslist()
page.get_car_results()

page = Ebay()
page.get_car_results()

analyzer = Analyzer()
analyzer.plot_results()