import glob
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class Analyzer(object):
	
	def __init__(self):
		self.data = self.merge_results()
		
		if 'Mileage' in self.data.columns:
			self.file_type = "Automobile"
		else:
			self.file_type = "Apartment"
	
	def merge_results(self):
		all_data = pd.DataFrame()
		files = glob.glob(".\\Data\\*.csv")  # Get csv files in data folder

		for filename in files:
			df = pd.read_csv(filename)
			all_data = all_data.append(df)

		all_data = all_data.dropna(axis=1, how='all')  # Remove Null Columns
		all_data.to_csv("MergedData.csv", index=False)
		return all_data

	def plot_results(self):
	
		fig = plt.figure(figsize=(13,6))
		if self.file_type == "Automobile":
			cols = ['Mileage', 'Price', 'Year', 'Link']
			self.data.Mileage.replace([',', 'mi.', 'nan', ' '], '', regex=True, inplace = True)  # Replace all empty values with np.NaN
			
			plt.xlabel('Mileage')
			plt.title('Mileage vs Cost (Year in Color)')
		else:
			cols = ['Area', 'Price', 'Bedrooms', 'Link']
			self.data['Area'] = self.data['Area'].map(lambda x: str(x)[:-3])
			
			plt.xlabel('Square Feet')
			plt.title('SqFt vs Cost (Number of Bedrooms in Color)')
		
		new_df = self.data[cols]
		new_df.dropna(axis=0, how='any', inplace=True)  # Remove rows with missing values
		new_df.Price.replace([',', '\$'], '', regex=True, inplace=True)  # Alwats fix price (, and $ removed)
		new_df.replace('^\s*$', np.nan, regex=True, inplace = True)  # Replace all empty values with np.NaN
		new_df[cols[:-1]] = new_df[cols[:-1]].apply(pd.to_numeric)
		
		s = plt.scatter(x=new_df[cols[0]], y=new_df[cols[1]], c=new_df[cols[2]], cmap='plasma')
		s.set_urls(new_df['Link'].values)
		plt.colorbar()
		plt.grid(which='both')
		plt.ylabel('Cost')
		plt.title('Mileage vs Cost (Year in Color)')
		plt.show()
		fig.canvas.print_figure('MergedData.svg')