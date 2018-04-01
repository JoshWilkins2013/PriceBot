import time
from selenium import webdriver


class Browser(object):
	""" Need to fix to make better - consider singleton?? """
	
	def __init__(self, url=None):
		self.driver = webdriver.Chrome()
		if url:
			self.driver.get(url)
	
	def wait_for_document_is_ready(self, timeout=3):

		def check_ready():
			state = self.driver.execute_script('return document.readyState;')
			if state != "complete":
				return False
			try:
				active = self.driver.execute_script('return jQuery.active;')
				return False
			except:
				return True

		def check_angular_requests_done():
			try:
				activeAngular = self.driver.execute_script('return angular.element(document).injector().get(\'$http\').pendingRequests.length;')
				return False
			except:
				return True
		
		def wait_until_no_error(timeout, wait_func, *args):
			max_time = time.time() + float(timeout)
			ready = wait_func(*args)
			while ( (time.time() < max_time) and not ready):
				ready = wait_func(*args)
				time.sleep(0.1)
		
		wait_until_no_error(timeout, check_ready)
		wait_until_no_error(timeout, check_angular_requests_done)
	
	def find_element(self, xpath, parent=None):
		try:
			if parent:
				return parent.find_element_by_xpath(xpath)
			else:
				return self.driver.find_element_by_xpath(xpath)
		except:
			return ''

	def click_button(self, xpath, parent=None):
		button = self.find_element(xpath, parent)
		if button is not '':
			button.click()
			self.wait_for_document_is_ready()
	
	def set_element_text(self, xpath, text, parent=None):
		element = self.find_element(xpath, parent)
		element.send_keys(text)
	
	def get_element_text(self, xpath, parent=None):
		element = self.find_element(xpath, parent)
		if element is not '':
			return element.text
		return ''

	def get_element_attribute(self, xpath, attr, parent=None):
		element = self.find_element(xpath, parent)
		if element is not '':
			return element.get_attribute(attr)
		return ''