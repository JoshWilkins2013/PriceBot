from Page import Page


class Ebay(Page):

	def __init__(self):
		self._zip = None
		self._radius = None

		Page.__init__(self, "https://www.ebay.com/sch/6001/i.html?&_sadis=&_stpos=&_nkw=+&LH_BIN=1&_ipg=200")

	def _get_page_ads(self):
		""" Get ads just on this page """
		ads_info = []
		ads = self.bro.driver.find_elements_by_xpath("//li[contains(@class,'lvresult clearfix li')]")
		for ad in ads:
			title = ad.find_element_by_xpath(".//h3[@class='lvtitle']//a").text
			if not title: break  # Don't get non-regional / international ones
			link = ad.find_element_by_xpath(".//h3[@class='lvtitle']//a").get_attribute("href")
			year = self.get_year(title)

			price = ad.find_element_by_xpath(".//li[@class='lvprice prc']").text
			price = int(float(price[1:].replace(',', '')))

			ad_info = {"Title": title, "Year": year, "Price": price, "Link": link}
			ads_info.append(ad_info)
		return ads_info

	def _get_ads(self):
		""" Get all ads across each page """
		ads_info = self._get_page_ads()
		count = self.bro.driver.find_element_by_xpath("//span[@class='rcnt']")
		if int(count.text.replace(',', '')) > 200:
			for x in range(int(count.text.replace(',', '')) / 200):
				self.bro.driver.find_element_by_xpath("//td[@class='pagn-next']").click()
				ads_info.extend(self._get_page_ads())

		return ads_info

	def get_car_results(self):
		i = 0
		ads_info = self._get_ads()
		for ad in ads_info:
			print len(ads_info) - i  # Some indication of progress
			self.bro.driver.get(ad['Link'])  # Go to ad link
			attributes = self.get_attrs()
			for cat, val in attributes.iteritems():
				ad[cat] = val
			i += 1
			
		self.bro.driver.close()

		# Save data to csv file
		self.write_to_csv('Ebay', ads_info)
		
	def get_state(self):
		""" Get location information (state) """
		infoLabels = self.bro.driver.find_elements_by_xpath("//div[@class='u-flL lable']")
		for label in infoLabels:
			if label.text == "Item location:":
				val = label.find_element_by_xpath("..//div[@class='u-flL']")
				val_text = val.text
				items = val_text.split(',')
				if len(items) == 3:
					return items[1].strip()
		return ''
	
	def get_attrs(self):
		attributes = {"State":self.get_state()}
		attrLabels = self.bro.driver.find_elements_by_xpath("//div[@class='itemAttr']//table[not(@id='itmSellerDesc')]//td")
		i = 0
		
		cats = []
		vals = []
		for attr in attrLabels:
			if (i%2)==1:
				val = attr.text
				vals.append(val)
			else:
				cat = attr.text[:-1]
				cats.append(cat)
			i += 1
		
		for cat, val in zip(cats, vals):
			attributes[cat] = val
		
		return attributes

	def change_link(self, part, value):
		link = self.bro.driver.current_url
		index = link.find(part) + len(part)
		new_link = link[:index] + value + link[index:]
		self.bro.driver.get(new_link)
	
	@property
	def make(self):
		return self._make
	@make.setter
	def make(self, user_make):
		self.change_link('_nkw=', user_make)
		self._make = user_make
			
	@property
	def model(self):
		return self._model
	@model.setter
	def model(self, user_model):
		self.change_link('+', user_model)
		self._model = user_model

	@property
	def radius(self):
		return self._radius
	@radius.setter
	def radius(self, user_radius):
		self.change_link('_sadis=', user_radius)
		self._radius = user_radius
	
	@property
	def zip(self):
		return self._zip
	@zip.setter
	def zip(self, user_zip):
		self.change_link('_stpos=', user_zip)
		self._zip = user_zip