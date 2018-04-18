from ..Browser import Browser
from ..Item import Item


class Page(Item):

	def __init__(self, url=None, page_name=''):

		if url:
			self.bro = Browser(url)
		else:
			self.bro = Browser()

		self.page_name = page_name

		Item.__init__(self)