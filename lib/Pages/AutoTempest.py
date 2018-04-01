import time
from Page import Page


class AutoTempest(Page):
	
	def __init__(self):
		Page.__init__(self, "https://www.autotempest.com")
	
	def get_car_results(self):
		self.bro.click_button("//form[@id='search-main']//button[@type='submit']")  # Submit Button
		time.sleep(1) # Obnoxious but page closes if this isn't here
		self.bro.click_button("//button[@class='change-sources show-box']")  # Sources Button
		self.bro.click_button("//span[@class='checkboxWrap eba mash']")  # Ebay Auctions Button
		self.bro.click_button("//button[@class='update-results']")  # Update Button

		ads_info = []
		ads = self.get_ads()
		for ad in ads:
			print len(ads) - len(ads_info)  # Some indication of progress
			title = self.bro.get_element_text(".//div[@class='description-wrap']//h2//a", parent=ad)  # Ad Title
			link = self.bro.get_element_attribute(".//div[@class='description-wrap']//h2//a", "href", parent=ad)  # Ad Link
			
			year = self.get_year(title)  # Get year from title text
			
			price = self.bro.get_element_text(".//div[@class='price']", parent=ad)  # Ad Price
			mileage = self.bro.get_element_text(".//span[@class='info mileage']", parent=ad)  # Ad Mileage
			
			ad_info = {"Title":title, "Year":year, "Mileage":mileage, "Price":price, "Link":link}
			ads_info.append(ad_info)  # Keep track of all Ad Information

		self.bro.driver.close()

		# Save data to csv file
		self.write_to_csv("AutoTempest", ads_info)
	
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