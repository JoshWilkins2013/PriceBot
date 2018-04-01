from lib.Pages import Craigslist

page = Craigslist()

ads_info = []
ads = page.get_ads()
for ad in ads:
	print len(ads_info)  # Some indication of progress
	title = ad['name']
	link = ad['url']
	price = ad['price'][1:]
	#date = ad['datetime']
	
	year = page.get_year(title)  # Get year from title text
	
	page.bro.driver.get(link)  # Go to page link
	
	attrs = page.bro.driver.find_elements_by_xpath("//p[@class='attrgroup']//span")
	attr_texts = [attr.text for attr in attrs]
	attrs_to_keep = ["condition", "odometer", "color", "transmission", "type"]
	
	ad_info = {"Title":title, "Link":link, "Price":price}
	for attr in attr_texts:
		key = next((attr.split(':')[0].strip() for x in attr.split(':')[0].strip().split() if x in attrs_to_keep), '')
		if key:
			value = next((attr.split(':')[1].strip() for x in attr.split(':')[0].strip().split() if x in attrs_to_keep), '')
			ad_info[key] = value
	
	ads_info.append(ad_info)

page.bro.driver.close()

# Save data to csv file
page.write_to_csv("Craigslist", ads_info)