import os
import pandas as pd


def get_year(title):
	""" Get year from title text """
	try:
		nums = [int(s) for s in title.replace(',', '').split() if s.isdigit()]  # Numbers in Ad Title
		year = [i for i in nums if 1985 <= int(i) <= 2018][0]  # Year from Ad Title
		return year
	except:
		return ''


def write_to_csv(data, fname):
	""" Write data to csv file """
	df = pd.DataFrame(data=data)
	df.apply(pd.to_numeric, errors='ignore')  # Coerces errors into NaN values

	if not os.path.exists(".\\Data"):
		os.makedirs(".\\Data")

	df.to_csv(".\\Data\\" + fname, encoding='utf-8', index=False)
