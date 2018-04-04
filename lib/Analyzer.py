import os
import glob
import numpy as np
import pandas as pd
from itertools import groupby
from matplotlib import pyplot as plt


class Analyzer(object):
	
	def __init__(self):
		self.merge_results()
	
	def _clean_results(self):
		""" Clean up some of the columns to be consistent """
		if self.file_type == "Automobile":
			self.data.Mileage.replace([',', 'mi.', 'nan', ' '], '', regex=True, inplace = True)  # Fix mileage column
		else:
			self.data.Area = self.data.Area.map(lambda x: str(x)[:-3])  # Fix square footage column
		
		self.data.Price.replace([',', '\$'], '', regex=True, inplace=True)  # Always fix price column (, and $ removed)
		self.data.replace('^\s*$', np.nan, regex=True, inplace = True)  # Replace all empty values with np.NaN
		self.data = self.data.dropna(axis=1, how='all')  # Remove Null Columns
		
		self.data.apply(pd.to_numeric, errors='coerce') # Coerces errors into NaN values
	
	def get_data(self, dir='.\\Data\\'):
		""" Gather & sort data by item name in Data folder
		return: An ordered dictionary {Item : [list of files]}
		"""
		# Get list of data files
		csv_files = glob.glob(dir + "*.csv")
		
		# Groups list into dictionary-like object by SN #
		item_groups = groupby(csv_files, lambda x: x[:x.find('_')])
		item_groups = dict( (item, list(files)) for (item, files) in item_groups )
		
		return item_groups
	
	def merge_results(self):
		self.data = pd.DataFrame()
		item_groups = self.get_data()
		
		for item, file_group in item_groups.iteritems():
			item_data = pd.DataFrame()
			for file_name in file_group:
				df = pd.read_csv(file_name)
				item_data = item_data.append(df)
				
			item_data.to_csv(item + "_Merged.csv", index=False)
			self.data = self.data.append(item_data)
			
			# Now that we know the data is safely stored, remove the old stuff
			for file_name in file_group:
				os.remove(file_name)
		
		if 'Mileage' in self.data.columns:
			self.file_type = "Automobile"
		else:
			self.file_type = "Apartment"
		
		self._clean_results()
		self.data.to_csv("MergedData.csv", index=False)

	def plot_results(self):
	
		fig = plt.figure(figsize=(13,6))
		
		if self.file_type == "Automobile":
			cols = ['Mileage', 'Price', 'Year', 'Link']
			plt.xlabel('Mileage')
			plt.title('Mileage vs Cost (Year in Color)')
		else:
			cols = ['Area', 'Price', 'Bedrooms', 'Link']
			plt.xlabel('Square Feet')
			plt.title('SqFt vs Cost (Number of Bedrooms in Color)')
		
		new_df = self.data[cols]
		new_df = new_df.dropna(axis=0, how='any')  # Remove rows with missing values
		
		for col in cols[:-1]:
			new_df[col] = new_df[col].astype(int)
		
		s = plt.scatter(x=new_df[cols[0]], y=new_df[cols[1]], c=new_df[cols[2]], cmap='plasma')
		s.set_urls(new_df['Link'].values)
		plt.colorbar()
		plt.grid(which='both')
		plt.ylabel('Cost')
		plt.title('Mileage vs Cost (Year in Color)')
		plt.show()
		fig.canvas.print_figure('MergedData.svg')