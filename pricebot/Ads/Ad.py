import pandas as pd


class Ad:
    def __init__(self, ad):
        self.ad = ad

        self.link = None
        self.title = None
        self.price = None

    def to_dict(self):
        return {
            name.capitalize(): value for name, value in self.__dict__.items()
            if name not in ['ad', 'title_tag', 'meta_tag']
        }

    def to_series(self):
        return pd.Series(self.to_dict())
