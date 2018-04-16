import os
import glob
import numpy as np
import pandas as pd
from itertools import groupby
from matplotlib import pyplot as plt

from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline


class Analyzer(object):

	def __init__(self):
		self.data = {}
		self.merge_results()
		self.items = self.data.keys()

	def _clean_results(self):
		""" Clean up some of the columns to be consistent """
		for item, item_data in self.data.iteritems():
			if self.file_type == "Automobile":
				cols = ["Year", "Mileage", "Price"]
				item_data.Mileage.replace([',', 'mi.', 'nan', ' '], '', regex=True, inplace = True)  # Fix mileage column
				item_data.Price.replace([',', '\$'], '', regex=True, inplace=True)  # Always fix price column (, and $ removed)
				item_data[cols] = item_data[cols].apply(pd.to_numeric, errors='coerce')  # Coerces errors into NaN values
				item_data.drop(item_data[item_data.Year < 2000].index, inplace=True) # Remove cars made before 2000
				item_data.drop(item_data[item_data.Price > 30000].index, inplace=True) # Remove cars over 30,000
				item_data.drop(item_data[(item_data.Mileage < 1000) | (item_data.Mileage > 300000)].index, inplace=True) # Remove cars with over 300,000 miles

				item_data['Age'] = 2018 - item_data['Year'] # Change years to Age
				del item_data['Year']
			else:
				item_data.Area.replace(['ft2'], '', regex=True, inplace=True)  # Remove ft2 from square footage column
				item_data.Price.replace([',', '\$'], '', regex=True, inplace=True)  # Always fix price column (, and $ removed)
				item_data.drop(item_data[item_data.Price > 2500].index, inplace=True) # Remove cars made before 2000
			
			item_data.replace('^\s*$', np.nan, regex=True, inplace = True)  # Replace all empty values with np.NaN
			item_data = item_data.dropna(axis=1, how='all')  # Remove Null Columns
			item_data = item_data.apply(pd.to_numeric, errors='coerce') # Coerces errors into NaN values

	def _get_data_groups(self, dir='.\\Data\\'):
		""" Gather & sort data by item name in Data folder
		return: An ordered dictionary {Item : [list of files]}
		"""

		item_groups = groupby(self._get_data(dir), lambda x: x[:x.find('_')])
		item_groups = dict( (item, list(files)) for (item, files) in item_groups )

		return item_groups

	def _get_data(self, dir='.\\Data\\'):
		""" Get list of data files """
		return glob.glob(dir + "*.csv")

	def merge_results(self):
		item_groups = self._get_data_groups()

		for item, file_group in item_groups.iteritems():
			item_data = pd.DataFrame()
			for file_name in file_group:
				df = pd.read_csv(file_name)
				item_data = item_data.append(df)

			item_data.to_csv(item + "_Merged.csv", index=False)
			self.data[item[7:]] = item_data

			# Now that we know the data is safely stored, remove the old stuff
			for file_name in file_group:
				if "Merged" in file_name: continue
				os.remove(file_name)

		if 'Mileage' in item_data.columns:
			self.file_type = "Automobile"
		else:
			self.file_type = "Apartment"

		self._clean_results()

	def merge_all_data(self):
		""" Merges all data into same csv file """
		csv_files = self._get_data()

		all_data = pd.DataFrame()
		for file_name in csv_files:
			temp_df = pd.read_csv(file_name)
			all_data.append(temp_df)

		all_data.to_csv("AllData_Merged.csv", index=False)

		# Now that we know the data is safely stored, remove the old stuff
		for file_name in csv_files:
			if "Merged" in file_name: continue
			os.remove(file_name)

	def _poly_fit(self, degree=2, **kwargs):
		return make_pipeline(PolynomialFeatures(degree), LinearRegression(**kwargs))

	def best_fit(self, item, col='Age', verbose=False):

		param_grid = {'polynomialfeatures__degree': np.arange(2, 3, 1),
					  'linearregression__fit_intercept': [True, False],
					  'linearregression__normalize': [True, False]}
		
		plt.subplot(1,2,1)
		if col == 'Age':
			group = self.data[item].groupby(self.data[item][col])[['Price']].mean().reset_index()[col].values
			mean_costs = self.data[item].groupby(self.data[item][col])[['Price']].mean().reset_index()['Price'].values
			median_costs = self.data[item].groupby(self.data[item][col])[['Price']].median().reset_index()['Price'].values
			metric = ((mean_costs + median_costs)/2)

			X_test = np.linspace(group[0], group[-1], len(group)+2)[:, None]
			X = group.reshape(len(group),1)
			y = metric
			plt.xlim(xmin=0, xmax=18)
		else:
			temp_df = self.data[item][[col, "Price"]].dropna(axis=0, how='any')  # Remove rows with missing values
			X = temp_df[col].values.reshape(len(temp_df),1)
			y = temp_df["Price"].values
			X_test = np.linspace(min(temp_df[col]), max(temp_df[col]), 1000)[:, None]
			plt.xlim(xmin=0, xmax=250000)

		grid = GridSearchCV(self._poly_fit(), param_grid)
		grid.fit(X, y)

		model = grid.best_estimator_

		if verbose:
			plt.scatter(X.ravel(), y)

		y_test = model.fit(X, y).predict(X_test)
		plt.plot(X_test.ravel(), y_test, label=item)

		plt.ylim(ymin=0, ymax=25000)
		plt.title(col + ' vs Cost')
		plt.grid(which='both')
		plt.legend()

		# Plot its derivative too - Shows depreciation rate better
		plt.subplot(1,2,2)
		best_order = grid.best_params_["polynomialfeatures__degree"]
		coeffs = np.polyfit(X.ravel(), y, best_order)

		p = np.poly1d(np.negative(coeffs))
		if col == 'Mileage':
			p *= 10000 # Convert derivative to $ per 10,000 miles instead of $ per mile
			plt.xlim(xmin=0, xmax=300000)
		else:
			plt.xlim(xmin=0, xmax=18)

		p2 = np.polyder(p)
		plt.plot(X_test.ravel(), p2(X_test.ravel()), label=item)

		plt.ylim(ymin=0, ymax=3000)
		plt.title(col + ' vs Cost')
		plt.grid(which='both')
		plt.legend()
		return coeffs

	def plot_results(self, item):

		fig = plt.figure(figsize=(13,6))

		if self.file_type == "Automobile":
			cols = ['Mileage', 'Price', 'Age', 'Link']
			plt.xlabel('Mileage')
			plt.title('Mileage vs Cost (Age in Color)')
		else:
			cols = ['Area', 'Price', 'Bedrooms', 'Link']
			plt.xlabel('Square Feet')
			plt.title('SqFt vs Cost (Number of Bedrooms in Color)')

		new_df = self.data[item][cols]
		new_df = new_df.dropna(axis=0, how='any')  # Remove rows with missing values

		for col in cols[:-1]:
			new_df[col] = new_df[col].astype(int)

		s = plt.scatter(x=new_df[cols[0]], y=new_df[cols[1]], c=new_df[cols[2]], cmap='plasma_r')
		s.set_urls(new_df['Link'].values)
		plt.colorbar()
		plt.grid(which='both')
		plt.ylabel('Cost')
		plt.show()
		fig.canvas.print_figure('MergedData.svg')
	
	def get_best_cars(self, item):
	
		for i in range(4):
			# Remove things above Mileage line of best fit
			coeffs = self.best_fit(item, 'Mileage')
			p = np.poly1d(coeffs)
			plt.clf()
			plt.scatter(x=self.data[item]['Mileage'], y=self.data[item]['Price'], cmap='plasma_r')
			self.data[item] = self.data[item][self.data[item]['Price'] < p(self.data[item]['Mileage'])]
			
			plt.plot(self.data[item]['Mileage'], p(self.data[item]['Mileage']), 'ro')
			plt.show()
			
			# Remove things above Age line of best fit
			# coeffs = self.best_fit(item, 'Age')

			# p = np.poly1d(coeffs)
			# plt.clf()
			# plt.scatter(x=self.data[item]['Age'], y=self.data[item]['Price'], cmap='plasma_r')
			# self.data[item] = self.data[item][self.data[item]['Price'] < p(self.data[item]['Age'])]
			
			# plt.plot(self.data[item]['Age'], p(self.data[item]['Age']), 'ro')
			# plt.show()
		
		plt.close()
		#self.plot_results(item)
		fig = plt.figure(figsize=(13,6))
		s = plt.scatter(self.data[item]['Age'], y=self.data[item]['Price'])
		s.set_urls(self.data[item]['Link'].values)
		plt.show()
		fig.canvas.print_figure('MergedData.svg')