import os
import glob
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline


class Analyzer(object):

	def __init__(self, file_path=".\\Data\\", file_name=None, file_type="Automobile", last_update=None):
		self.file_path = file_path
		self.file_name = file_name
		self.file_type = file_type
		self.last_update = last_update

		if file_name:
			if file_type == 'Automobile':
				self.car = self.file_name[:self.file_name.find('_')]
			self.data = pd.read_csv(self.file_path + self.file_name)
			self._clean_results()
		else:
			self.data = None

	def _clean_results(self):
		""" Clean up some of the columns to be consistent """
		if self.file_type == "Automobile":
			cols = ["Year", "Mileage", "Price"]
			self.data.Mileage.replace([',', 'mi.', 'nan', ' '], '', regex=True, inplace=True)  # Fix mileage column
			self.data.Price.replace([',', '\$'], '', regex=True, inplace=True)  # Always fix price column (, and $ removed)
			self.data[cols] = self.data[cols].apply(pd.to_numeric, errors='coerce')  # Coerces errors into NaN values
			self.data.drop(self.data[self.data.Year < 2000].index, inplace=True)  # Remove cars made before 2000
			self.data.drop(self.data[self.data.Price > 30000].index, inplace=True)  # Remove cars over $30,000
			self.data.drop(self.data[(self.data.Mileage < 1000) | (self.data.Mileage > 300000)].index, inplace=True)  # Remove cars with over 300,000 miles
			self.data['Age'] = 2018 - self.data['Year']  # Change years to Age
		elif self.file_type == "Apartment":
			self.data.Area.replace(['ft2'], '', regex=True, inplace=True)  # Remove ft2 from square footage column
			self.data.Price.replace([',', '\$'], '', regex=True, inplace=True)  # Always fix price column (, and $ removed)
		else:
			self.data['Street'], self.data['City'], self.data['State'] = self.data['Address'].str.split(',', 2).str
			del self.data.Address
			self.data.drop(self.data[self.data.Price > 1000000].index, inplace=True)  # Remove houses worth more than $1 million

		self.data.replace('^\s*$', np.nan, regex=True, inplace=True)  # Replace all empty values with np.NaN
		self.data = self.data.dropna(axis=1, how='all')  # Remove Null Columns
		self.data = self.data.apply(pd.to_numeric, errors='ignore')  # Coerces errors into NaN values

	def merge_results(self, car):
		self.car = car
		data_files = glob.glob(self.file_path + self.car + '*.csv')

		item_data = pd.DataFrame()
		for data_file in data_files:
			df = pd.read_csv(data_file)
			item_data = item_data.append(df)

		self.file_name = self.car + "_Merged.csv"
		item_data.to_csv(self.file_path + self.file_name, index=False)
		self.data = item_data
		self._clean_results()

	def plot_results(self):
		fig = plt.figure(figsize=(13, 6))

		if self.file_type == "Automobile":
			cols = ['Mileage', 'Price', 'Age', 'Link']
			plt.xlabel('Mileage')
			plt.title('Mileage vs Cost (Age in Color)')
		elif self.file_type == 'Apartment':
			cols = ['Area', 'Price', 'Link']
			plt.xlabel('Square Feet')
			plt.title('SqFt vs Cost (Number of Bedrooms in Color)')
		else:
			return

		new_df = self.data[cols]
		new_df = new_df.dropna(axis=0, how='any')  # Remove rows with missing values

		for col in cols[:-1]:
			new_df[col] = new_df[col].astype(int)

		s = plt.scatter(x=new_df[cols[0]], y=new_df[cols[1]])
		s.set_urls(new_df['Link'].values)
		plt.grid(which='both')
		plt.ylabel('Cost')
		plt.show()
		fig.canvas.print_figure('MergedData.svg')

	def get_best_cars(self, filter_by='Mileage', n_iter=4, last_update=None, filtered_data=None, plot_show=False):
		for i in range(n_iter):
			# Remove things above Age line of best fit
			coeffs = self.best_fit(col=filter_by)

			p = np.poly1d(coeffs)
			plt.clf()
			plt.scatter(x=self.data[filter_by], y=self.data['Price'], cmap='plasma_r')
			self.data = self.data[self.data['Price'] < p(self.data[filter_by])]  # Remove points above average price trendline

			plt.plot(self.data[filter_by], p(self.data[filter_by]), 'ro')  # Average price trendline by age/mileage
			if filtered_data is not None:
				plt.scatter(x=filtered_data[filter_by], y=filtered_data['Price'], cmap='plasma_r')
			plt.xlabel('filter_by')
			plt.ylabel('Price')
			if plot_show:
				plt.show()

		plt.close()

		fig = plt.figure(figsize=(13, 6))

		s = plt.scatter(self.data[filter_by], y=self.data['Price'], color='blue')
		s.set_urls(self.data['Link'].values)

		# Color cars that meet filter green
		if filtered_data is not None:
			filtered_merged = pd.merge(filtered_data, self.data, how='inner')  # Not sure why I have to do this
			s = plt.scatter(x=filtered_merged[filter_by], y=filtered_merged['Price'], color='green')
			s.set_urls(filtered_merged['Link'].values)

		# Color cars that are new red
		if self.last_update is not None:
			self.data['Date'] = pd.to_datetime(self.data['Date'], format='%Y-%m-%d %H:%M')
			recent_data = self.data[self.data['Date'] > self.last_update]
			recent_merged = pd.merge(recent_data, self.data, how='inner')  # Not sure why I have to do this
			s = plt.scatter(x=recent_merged[filter_by], y=recent_merged['Price'], color='red')
			s.set_urls(recent_merged['Link'].values)

		if plot_show:
			plt.show()

		if not os.path.exists(".\\Best" + filter_by):
			os.makedirs(".\\Best" + filter_by)

		fig.canvas.print_figure(".\\Best" + filter_by + "\\" + self.file_name[:-4] + '.svg')

	def best_fit(self, col='Age', verbose=False):

		param_grid = {'polynomialfeatures__degree': np.arange(2, 3, 1),
						'linearregression__fit_intercept': [True, False],
						'linearregression__normalize': [True, False]}
		
		plt.subplot(1, 2, 1)
		if col == 'Age':
			group = self.data.groupby(self.data['Age'])[['Price']].mean().reset_index()['Age'].values
			mean_costs = self.data.groupby(self.data['Age'])[['Price']].mean().reset_index()['Price'].values
			median_costs = self.data.groupby(self.data['Age'])[['Price']].median().reset_index()['Price'].values
			metric = ((mean_costs + median_costs)/2)

			X_test = np.linspace(group[0], group[-1], len(group)+2)[:, None]
			X = group.reshape(len(group), 1)
			y = metric
			plt.xlim(xmin=0, xmax=18)
		else:
			temp_df = self.data[[col, "Price"]].dropna(axis=0, how='any')  # Remove rows with missing values
			X = temp_df[col].values.reshape(len(temp_df), 1)
			y = temp_df["Price"].values
			X_test = np.linspace(min(temp_df[col]), max(temp_df[col]), 1000)[:, None]
			plt.xlim(xmin=0, xmax=250000)

		grid = GridSearchCV(make_pipeline(PolynomialFeatures(2), LinearRegression()), param_grid)
		grid.fit(X, y)

		model = grid.best_estimator_

		if verbose:
			plt.scatter(X.ravel(), y)

		y_test = model.fit(X, y).predict(X_test)
		plt.plot(X_test.ravel(), y_test, label=self.car)

		plt.ylim(ymin=0, ymax=25000)
		plt.title(col + ' vs Cost')
		plt.grid(which='both')
		plt.legend()

		# Plot its derivative too - Shows depreciation rate better
		plt.subplot(1, 2, 2)
		best_order = grid.best_params_["polynomialfeatures__degree"]
		coeffs = np.polyfit(X.ravel(), y, best_order)

		p = np.poly1d(np.negative(coeffs))
		if col == 'Mileage':
			p *= 10000 # Convert derivative to $ per 10,000 miles instead of $ per mile
			plt.xlim(xmin=0, xmax=300000)
		else:
			plt.xlim(xmin=0, xmax=18)

		p2 = np.polyder(p)
		plt.plot(X_test.ravel(), p2(X_test.ravel()), label=self.car)

		plt.ylim(ymin=0, ymax=3000)
		plt.title(col + ' vs Cost')
		plt.grid(which='both')
		plt.legend()
		
		# Add predicted value of data to csv file
		p = np.poly1d(coeffs)
		p2 = np.polyder(p)
		if col == 'Age':
			self.data['Price Diff Age'] = self.data['Age'] - p(self.data['Age'])
			self.data['Depreciate Age'] = p2(self.data['Age'])
		if col == 'Mileage':
			self.data['Price Diff Mileage'] = self.data['Mileage'] - p(self.data['Mileage'])
			self.data['Depreciate Mileage'] = p2(self.data['Mileage'])*10000

		return coeffs
