from pricebot.Analyzer import Analyzer
from pricebot.Pages.Zillow import Zillow

# Danvers: 01923
# Salem: 01970
# Beverly: 01915

zips = ["01923", "01915", "01970"]

for zip in zips:
	page = Zillow(zip)
	page.get_house_results()

az = Analyzer()
az.merge_all_data()
az._clean_results()
az.plot_results("All_Data")