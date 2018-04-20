import os
import time
import pandas as pd


class Item(object):

	def __init__(self, item_type="Automobile", **kwargs):
		self.item_type = item_type
		print ''

		if item_type == "Automobile":
			user_make = raw_input("Make: ").capitalize()
			user_model = raw_input("Model: ").capitalize()

			self.make = user_make
			time.sleep(1)  # Needed for AutoTempest -- should fix this somehow
			self.model = user_model

			#self.make = kwargs.get('make', '')
			#self.model = kwargs.get('model', '')

		if not self.zip:
			self.zip = raw_input("Zip: ")
		if not self.radius:
			self.radius = raw_input("Radius: ")

		#self.radius = kwargs.get('radius', '')
		#self.zip = kwargs.get('zip_code', '')

	def get_year(self, title):
		""" Get year from title text """
		try:
			nums = [int(s) for s in title.replace(',', '').split() if s.isdigit()]  # Numbers in Ad Title
			year = [i for i in nums if 1985 <= int(i) <= 2018][0]  # Year from Ad Title
			return year
		except:
			return ''

	def write_to_csv(self, suffix, data):
		""" Write data to csv file """
		df = pd.DataFrame(data=data)
		df.apply(pd.to_numeric, errors='coerce')  # Coerces errors into NaN values

		if self.item_type == "Automobile":
			fname = self.make + self.model + '_' + suffix + '.csv'
		elif self.item_type == "Housing":
			fname = self.zip + "_Zillow.csv"
		else:
			fname = 'Apts_' + suffix + '.csv'

		if not os.path.exists(".\\Data"):
			os.makedirs(".\\Data")

		df.to_csv(".\\Data\\" + fname, encoding='utf-8', index=False)