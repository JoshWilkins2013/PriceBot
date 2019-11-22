import pandas as pd
from ..Item import *
from ..Browser import Browser
from datetime import datetime as dt
from craigslist import CraigslistForSale
from craigslist import CraigslistHousing


class Craigslist(object):

	def __init__(self, site="Boston"):
		self.site = site
		self.bro = None

		self.last_update = None

	def get_car_results(self, make=None, model=None, zip_code='01923', radius=50, overwrite=False):
		if not make:
			make = raw_input("Make: ").capitalize()
		if not model:
			model = raw_input("Model: ").capitalize()
		if not zip_code:
			zip_code = raw_input("Zip: ")
		if not radius:
			radius = raw_input("Radius: ")

		cl = CraigslistForSale(site=self.site.lower(), category='cta', filters={'zip_code': zip_code, 'search_distance': radius, 'query': make + ' ' + model, 'make': make, 'model': model, 'min_price': 500})
		ads = cl.get_results(sort_by='newest')

		fname = make + model + '_' + self.site + 'Craigslist.csv'

		# If data file already exists, only update it with new data (by grabbing latest date)
		if os.path.isfile(".\\Data\\" + fname):
			df = pd.read_csv(".\\Data\\" + fname, usecols=['Date'])
			df['Date'] = pd.to_datetime(df['Date'])
			self.last_update = str(max(df['Date']))
			print("Grabbing data after " + self.last_update)

		self.bro = Browser("https://" + self.site + ".craigslist.org/")

		ads_info = []
		for ad in ads:
			print len(ads_info)  # Some indication of progress
			ad_info = {}

			ad_info['Title'] = ad['name']
			ad_info['Link'] = ad['url']
			ad_info['Price'] = ad['price'][1:]
			ad_info['Date'] = ad['datetime']
			ad_info['Year'] = get_year(ad_info['Title'])  # Get year from title text

			self.bro.driver.get(ad_info['Link'])  # Go to page link

			if self.last_update:
				if dt.strptime(ad_info['Date'], "%Y-%m-%d %H:%M") <= dt.strptime(self.last_update, "%Y-%m-%d %H:%M:%S"):
					break  # If we already have the data, dont grab it again - stop the process, since its sorted by date

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
		if len(ads_info) > 0:
			if os.path.isfile(".\\Data\\" + fname) and not overwrite:
				temp_df = pd.read_csv(".\\Data\\" + fname)
				temp_df = temp_df.append(ads_info)
				write_to_csv(temp_df, fname)
			else:
				write_to_csv(ads_info, fname)

		return self.last_update

	def get_apt_results(self, zip_code='01923', radius=20, max_price=1600, sub_category=None, overwrite=False):
		cl = CraigslistHousing(site=self.site.lower(), category=sub_category + '/aap', filters={'zip_code': zip_code, 'search_distance': radius, 'min_price': 500, 'max_price': max_price})
		results = cl.get_results()

		# If data file already exists, only update it with new data (by grabbing latest date)
		fname = 'Apartments_' + self.site + 'Craigslist.csv'
		if not overwrite and os.path.isfile(".\\Data\\" + fname):
			with open(".\\Data\\" + fname) as f:
				self.last_update = f.readlines()[1].split(',')[2]
				print("Grabbing data after " + self.last_update)

		ads_info = []
		for result in results:
			print len(ads_info)  # Some indication of progress
			ad_info = {}

			def get_attr(ad, attr):
				try: return ad[attr]
				except: return ''

			ad_info['Title'] = get_attr(result, 'name')
			ad_info['Area'] = get_attr(result, 'area')
			ad_info['Bedrooms'] = get_attr(result, 'bedrooms')
			ad_info['Link'] = get_attr(result, 'url')
			ad_info['Price'] = get_attr(result, 'price')
			ad_info['Location'] = get_attr(result, 'geotag')
			ad_info['Date'] = get_attr(result, 'datetime')

			if self.last_update:
				if dt.strptime(ad_info['Date'], "%Y-%m-%d %H:%M") <= dt.strptime(self.last_update, "%Y-%m-%d %H:%M:%S"):
					break  # If we already have the data, dont grab it again - stop the process, since its sorted by date

			ads_info.append(ad_info)
		
		# Save data to csv file
		if len(ads_info) > 0:
			if os.path.isfile(".\\Data\\" + fname) and not overwrite:
				temp_df = pd.read_csv(".\\Data\\" + fname)
				temp_df = temp_df.append(ads_info)
				write_to_csv(temp_df, fname)
			else:
				write_to_csv(ads_info, fname)
