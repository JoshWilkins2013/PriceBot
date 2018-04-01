from lib.Pages import Ebay

page = Ebay()

ads_info = page.get_ads()
for ad in ads_info:
	page.bro.driver.get(ad['Link'])  # Go to ad link
	attributes = page.get_attrs()
	for cat, val in attributes.iteritems():
		ad[cat] = val
	
page.bro.driver.close()

# Save data to csv file
page.write_to_csv('Ebay', ads_info)