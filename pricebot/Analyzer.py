import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class Analyzer(object):
    def __init__(self, file_path=r".\Data", file_name=None, file_type="Automobile"):
        self.file_path = file_path
        self.file_name = file_name
        self.file_type = file_type

        if file_name:
            if file_type == 'Automobile':
                self.car = self.file_name[:self.file_name.find('_')]
            self.data = pd.read_csv(rf"{self.file_path}\{self.file_name}")
            self._clean_results()
        else:
            self.data = None

    def _clean_results(self):
        """ Clean up some of the columns to be consistent """
        if self.file_type == "Automobile":
            cols = ["Year", "Mileage", "Price"]
            self.data.Mileage = self.data.Mileage.replace([',', 'mi.', 'nan', ' '], '', regex=True)  # Fix mileage column
            self.data.Price = self.data.Price.replace([',', '$'], '', regex=True)  # Always fix price column (, and $ removed)
            self.data[cols] = self.data[cols].apply(pd.to_numeric, errors='coerce')  # Coerces errors into NaN values
            self.data['Mileage'] = self.data['Mileage'] * 1000  # Make in terms of actual mileage
            self.data.drop(self.data[self.data.Year < 2000].index, inplace=True)  # Remove cars made before 2000
            self.data.drop(self.data[self.data.Price > 30000].index, inplace=True)  # Remove cars over $30,000
            self.data.drop(self.data[(self.data.Mileage < 1000) | (self.data.Mileage > 300000)].index, inplace=True)  # Remove cars with over 300,000 miles
            self.data['Age'] = 2018 - self.data['Year']  # Change years to Age
        elif self.file_type == "Apartment":
            self.data.Area = self.data.area.replace(['ft2'], '', regex=True)  # Remove ft2 from square footage column
            self.data.Price = self.data.Price.replace([',', '$'], '', regex=True)  # Always fix price column (, and $ removed)
            self.data.Bedrooms = self.data.bedrooms.replace(['br', ''], '', regex=True)  # Always fix price column (, and $ removed)
        else:
            self.data['Street'], self.data['City'], self.data['State'] = self.data['Address'].str.split(',', 2).str
            del self.data.Address
            self.data.drop(self.data[self.data.Price > 1000000].index, inplace=True)  # Remove houses worth more than $1 million

        self.data = self.data.replace('^s*$', np.nan)  # Replace all empty values with np.NaN
        self.data = self.data.dropna(axis=1, how='all')  # Remove Null Columns
        self.data = self.data.apply(pd.to_numeric, errors='ignore')  # Coerces errors into NaN values

    def plot_results(self, show_figure=False):
        fig = plt.figure(figsize=(13, 6))

        if self.file_type == "Automobile":
            cols = ['Mileage', 'Price', 'Age', 'Link']
            plt.xlabel('Mileage')
            plt.title('Mileage vs Cost (Age in Color)')
        elif self.file_type == 'Apartment':
            cols = ['Price', 'Link']
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

        if show_figure:
            plt.show()

        fig.canvas.print_figure(rf"{self.file_path}\{self.file_name[:-4]}.svg")
