from pricebot.Analyzer import Analyzer
from pricebot.Pages.Craigslist import Craigslist

page = Craigslist()
page.get_apt_results()

az = Analyzer()
az._clean_results()
az.plot_results(az.items[0])