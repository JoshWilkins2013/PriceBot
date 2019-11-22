import re
import time
import zipcode
from ..Item import *
from ..Browser import Browser


class Zillow(object):

	def __init__(self, zip=None, radius=None):

		print ''

		self.zip = zip
		if not self.zip:
			self.zip = raw_input("Zip: ")

		self.radius = radius
		if not self.radius:
			self.radius = raw_input("Radius: ")

		self.bro = Browser("https://www.zillow.com/homes/for_sale/{0}_rb/house,condo,apartment_duplex,mobile,townhouse_type/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy".format(self.zip), item_type="Housing")

	def _get_ad_property(self, ad, xpath):
		try:
			raw_item = ad.find_element_by_xpath(xpath)
			return raw_item.text
		except:
			return

	def _get_ad_properties(self, ad):

		try:
			ad.find_element_by_xpath('.//span[@class="zsg-icon-for-sale"]')
		except:
			return  # If item not for sale, don't bother getting its data

		properties = {}
		properties["Address"] = self._get_ad_property(ad, ".//span[@class='zsg-photo-card-address']")

		price = self._get_ad_property(ad, ".//span[@class='zsg-photo-card-price']")
		if price:
			price = price.replace(',', '')  # Remove comma in sqrft so that we can more easily get the value
			properties["Price"] = re.findall(r"[-+]?\d*\.\d+|\d+", price)[0]  # Get all numbers from info
		else:
			properties["Price"] = ''

		info = self._get_ad_property(ad, ".//span[@class='zsg-photo-card-info']")
		info = info.replace(',', '')  # Remove comma in sqrft so that we can more easily get the value
		nums = re.findall(r"[-+]?\d*\.\d+|\d+", info)  # Get all numbers from info

		try:
			properties["Bedrooms"] = nums[0]
			properties["Bathrooms"] = nums[1]
			properties["Area"] = nums[2]
		except:
			pass

		properties["Broker"] = self._get_ad_property(ad, ".//span[@class='zsg-photo-card-broker-name']")
		properties["Title"] = self._get_ad_property(ad, ".//h4")

		link_element = ad.find_element_by_xpath(".//a[contains(@class,'overlay-link')]")
		properties["Link"] = link_element.get_attribute("href")

		return properties

	def get_house_results(self):

		zip_code = zipcode.isequal(self.zip)
		d = zip_code.to_dict()
		point = (d['lat'], d['lon'])
		zips = zipcode.isinradius(point, self.radius)
		zips = [new_zip for new_zip in zips if not new_zip.decommisioned != "FALSE"]
		zips = [new_zip.zip for new_zip in zips if new_zip.zip_type == "STANDARD"]

		ads_info = []
		for zip in zips:
			self.bro.driver.get("https://www.zillow.com/homes/for_sale/{0}_rb/house,condo,apartment_duplex,mobile,townhouse_type/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy".format(zip))

			try:
				next_button = self.bro.driver.find_element_by_xpath("//li[@class='zsg-pagination-next']")
			except:
				next_button = 'Something'

			while next_button:
				ads = self.bro.driver.find_elements_by_xpath("//div[@id='search-results']//article")

				for ad in ads:
					properties = self._get_ad_properties(ad)
					if properties:
						ads_info.extend([properties])

				try:
					next_button = self.bro.driver.find_element_by_xpath("//li[@class='zsg-pagination-next']")
					next_button.click()
				except:
					break
				time.sleep(2)  # Should get rid of this

		self.bro.driver.close()
		write_to_csv("Zillow", ads_info)