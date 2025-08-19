from pricebot.Analyzer import Analyzer
from pricebot.Pages.Facebook import Facebook
from pricebot.Pages.Craigslist import Craigslist

motorcycles = {
    "Ninja": ["650"],
    # "Toyota": ["Corolla"]
}

city = "Rochester"
site = "Facebook"

for make, models in motorcycles.items():  # changed iteritems() to items()
    for model in models:
        motorcycle = f"{make}{model}"
        print(motorcycle)

        # Rochester Results
        page = Craigslist(city) if site == "Craigslist" else Facebook(city)
        page.get_car_results(make, model, radius=50)

        # # Filter / plot results
        analyzer = Analyzer(file_path=r".\Data", file_name=f"{make}{model}_{city}{site}.csv")

        # # Permanent changes to data
        analyzer.data = analyzer.data[analyzer.data['Age'] < 13]
        analyzer.data = analyzer.data[analyzer.data['Price'] < 15000]
        analyzer.data = analyzer.data[analyzer.data['Mileage'] < 150000]

        analyzer.plot_results()
