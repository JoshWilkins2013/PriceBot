import os
import time
import pandas as pd
from ..Browser import Browser


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
	
	def write_to_csv(self, suffix, data, type="Automobile"):
		""" Write data to csv file """
		df = pd.DataFrame(data=data)
		df.apply(pd.to_numeric, errors='coerce') # Coerces errors into NaN values
		
		if type == "Automobile":
			fname = self.make + self.model + '_' + suffix + '.csv'
		else:
			fname = 'Apts_' + suffix + '.csv'
		
		if not os.path.exists(".\\Data"):
			os.makedirs(".\\Data")

		df.to_csv(".\\Data\\" + fname, encoding='utf-8', index=False)