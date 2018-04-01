import time
import pandas as pd
from Browser import Browser
from craigslist import CraigslistForSale
from selenium.webdriver.support.ui import Select

class Page(object):

	def __init__(self, url=None):
		print ''
		user_make = raw_input("Make: ").capitalize()
		user_model = raw_input("Model: ").capitalize()
		user_radius = raw_input("Radius: ")
		user_zip = raw_input("Zip: ")
		
		if url: self.bro = Browser(url)
		else: self.bro = Browser()
		
		self.make = user_make
		time.sleep(1)  # Needed for AutoTempest -- should fix this somehow
		self.model = user_model
		self.radius = user_radius
		self.zip = user_zip
	
	def get_year(self, title):
		""" Get year from title text """
		try:
			nums = [int(s) for s in title.replace(',', '').split() if s.isdigit()]  # Numbers in Ad Title
			year = [i for i in nums if 1985 <= int(i) <= 2018][0] # Year from Ad Title
			return year
		except:
			return ''
	
	def write_to_csv(self, suffix, data):
		""" Write data to csv file """
		df = pd.DataFrame(data=data)
		df = df.convert_objects(convert_numeric = True)
		fname = self.make + self.model + '_' + suffix + '.csv'
		df.to_csv(fname)


class Ebay(Page):
	""" Not fully tested """
	
	def __init__(self):
		Page.__init__(self, "https://www.ebay.com/sch/6001/i.html?&_sadis=&_stpos=&_nkw=+")
	
	def _get_page_ads(self):
		""" Get ads just on this page """
		ads_info = []
		ads = self.bro.driver.find_elements_by_xpath("//li[contains(@class,'lvresult clearfix li')]")
		for ad in ads:
			title = self.bro.get_element_text(".//h3[@class='lvtitle']//a")
			link = self.bro.get_element_attribute(".//h3[@class='lvtitle']//a", "href")
			year = self.get_year(title)
			
			price = self.bro.get_element_text(".//li[@class='lvprice prc']")
			price = int(float(price[1:].replace(',', '')))
			ad_info = {"Title":title, "Year":year, "Price":price, "Link":link}
			ads_info.append(ad_info)
		return ads_info
	
	def get_ads(self):
		""" Get all ads across each page """
		ads_info = self._get_page_ads()
		count = self.bro.driver.find_element_by_xpath("//span[@class='rcnt']")
		if int(count.text.replace(',', '')) > 200:
			for x in range(int(count.text.replace(',', ''))/200):
				self.bro.click_button("//td[@class='pagn-next']")
				ads_info.extend(self._get_page_ads())
		
		return ads_info
		
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
		attributes = {"State":self.get_state}
		attrLabels = self.bro.driver.find_elements_by_xpath("//div[@class='itemAttr']//table[not(@id='itmSellerDesc')]//td")
		i = 0
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


class Craigslist(Page):
	""" Test completed """

	def get_ads(self):
		query = self.make + ' ' + self.model
		cl = CraigslistForSale(site='boston', category='cta', filters={'query':query, 'make':self.make, 'model': self.model, 'min_price': 500})
		return cl.get_results(sort_by='newest')


class AutoTempest(Page):
	""" Works """
	
	def __init__(self):
		Page.__init__(self, "https://www.autotempest.com")
		
	def get_ads(self):
		more_buttons = self.bro.driver.find_elements_by_xpath("//button[@class='more-results']")  # More Buttons
		while more_buttons != []:
			for button in more_buttons:
				try: # Should check for visibility first to replace try statement
					button.click()
				except:
					pass
			more_buttons = self.bro.driver.find_elements_by_xpath("//button[@class='more-results']")
		return self.bro.driver.find_elements_by_xpath("//div[@class='result-wrap']")
	
	@property
	def make(self):
		return self._make
	@make.setter
	def make(self, user_make):
		makes = self.bro.driver.find_elements_by_xpath("//select[@id='make']//option")
		make_texts = [make.text for make in makes]
		if user_make in make_texts:
			makes[make_texts.index(user_make)].click()
			self.bro.wait_for_document_is_ready()
			self._make = user_make
			
	@property
	def model(self):
		return self._model
	@model.setter
	def model(self, user_model):
		models = self.bro.driver.find_elements_by_xpath("//select[@id='model']//option")
		model_texts = [model.text for model in models]
		if user_model in model_texts:
			models[model_texts.index(user_model)].click()
			self.bro.wait_for_document_is_ready()
			self._model = user_model
	
	@property
	def radius(self):
		return self._radius
	@radius.setter
	def radius(self, user_radius):
		radii = self.bro.driver.find_elements_by_xpath("//select[@id='radius']//option")
		radius_texts = [radius.text for radius in radii]
		
		if user_radius.capitalize() == "Any":
			radii[radius_texts.index(str("Any"))].click()
		else:
			temp_texts = [int(radius) for radius in radius_texts if radius != "Any"]
			radius = min(temp_texts, key = lambda x : abs(x-int(user_radius)))	# Grab closest radius value
			radii[radius_texts.index(str(radius))].click()
		
		self.bro.wait_for_document_is_ready()
		self._radius = user_radius
	
	@property
	def zip(self):
		return self._zip
	@zip.setter
	def zip(self, user_zip):
		zip = self.bro.driver.find_element_by_xpath("//input[@id='zip']")
		zip.send_keys(user_zip)
		self._zip = user_zip