from pricebot.Analyzer import Analyzer
from pricebot.Pages.Zillow import Zillow
# from pricebot.Pages.Apartments import Apartments

page = Apartments()
page.get_apt_results(city="Avon", state="Ny")

# page = Zillow()
# page.get_house_results()

# az = Analyzer()
# az.merge_all_data()
# az._clean_results()
# az.plot_results("All_Data")