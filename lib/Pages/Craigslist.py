from Page import Page
from craigslist import CraigslistForSale


class Craigslist(Page):

	def get_ads(self):
		query = self.make + ' ' + self.model
		cl = CraigslistForSale(site='boston', category='cta', filters={'query':query, 'make':self.make, 'model': self.model, 'min_price': 500})
		return cl.get_results(sort_by='newest')