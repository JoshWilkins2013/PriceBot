from Page import Page
from craigslist import CraigslistForSale
from craigslist import CraigslistHousing


class Craigslist(Page):

	def __init__(self):
		self.zip = None
		self.radius = None
		
		Page.__init__(self, "https://www.autotempest.com")

	def get_car_results(self):
		query = self.make + ' ' + self.model
		cl = CraigslistForSale(site='boston', category='cta', filters={'query':query, 'make':self.make, 'model': self.model, 'min_price': 500})
		ads = cl.get_results(sort_by='newest')
		
		ads_info = []
		for ad in ads:
			print len(ads_info)  # Some indication of progress
			ad_info = {}

			ad_info['Title'] = ad['name']
			ad_info['Link'] = ad['url']
			ad_info['Price'] = ad['price'][1:]
			ad_info['Date'] = ad['datetime']
			ad_info['Year'] = self.get_year(ad_info['Title'])  # Get year from title text
			
			self.bro.driver.get(ad_info['Link'])  # Go to page link
			
			attrs = self.bro.driver.find_elements_by_xpath("//p[@class='attrgroup']//span")
			attr_texts = [attr.text for attr in attrs]
			attrs_to_keep = ["condition", "odometer", "color", "transmission", "type"]
			
			for attr in attr_texts:
				key = next((attr.split(':')[0].strip() for x in attr.split(':')[0].strip().split() if x in attrs_to_keep), '')
				if key:
					try:
						value = next((attr.split(':')[1].strip() for x in attr.split(':')[0].strip().split() if x in attrs_to_keep), '')
						if key == "odometer":  # ToDo: Probably a better spot to put this
							key = "Mileage"
						ad_info[key] = value
					except:
						pass

			ads_info.append(ad_info)
			
		self.bro.driver.close()

		# Save data to csv file
		self.write_to_csv("Craigslist", ads_info)
	
	def get_apt_results(self):
		cl = CraigslistHousing(site='boston', category='aap', filters={'zip_code':self.zip, 'search_distance':self.radius})
		results = cl.get_results()

		ads_info = []
		for result in results:
			print len(ads_info)  # Some indication of progress
			ad_info = {}
			ad_info['Title'] = result['name']
			ad_info['Area'] = result['area']
			ad_info['Bedrooms'] = result['bedrooms']
			ad_info['Link'] = result['url']
			ad_info['Price'] = result['price'][1:]
			ad_info['Location'] = result['geotag']
			ad_info['Date'] = result['datetime']
			
			ads_info.append(ad_info)
		
		# Save data to csv file
		self.write_to_csv("Craigslist", ads_info)