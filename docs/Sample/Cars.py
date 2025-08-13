import os
import pandas as pd
from pricebot.Analyzer import Analyzer
from pricebot.Pages.Craigslist import Craigslist

cars = {
    "Honda": ["Civic"]
}

for make, models in cars.items():  # changed iteritems() to items()
    for model in models:
        car = f"{make}{model}"
        print(car)

        last_update = '7/19/2019  6:30:00 PM'
        file_path = os.path.join("Data", f"{car}_Merged.csv")

        if os.path.isfile(file_path):
            df = pd.read_csv(file_path, usecols=['Date'])
            df['Date'] = pd.to_datetime(df['Date'])
            last_update = str(df['Date'].max())

        # Rochester Results
        page = Craigslist("Rochester")
        page.get_car_results(make, model, '14414', 50)

        # # Filter / plot results
        # analyzer = Analyzer(file_path="Data", last_update=last_update)
        # # analyzer.merge_results(car)  # Merges boston and rochester - sets data variable in analyzer to merged file data

        # # Permanent changes to data
        # analyzer.data = analyzer.data[analyzer.data['Age'] < 13]
        # analyzer.data = analyzer.data[analyzer.data['Price'] < 8000]
        # analyzer.data = analyzer.data[analyzer.data['Mileage'] < 150000]

        # # Temporary changes to highlight better options
        # filtered_data = analyzer.data[analyzer.data['transmission'] == 'manual']

        # analyzer.get_best_cars(filter_by='Age', n_iter=0, filtered_data=filtered_data)