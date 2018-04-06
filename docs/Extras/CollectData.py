import os
import glob
import pandas as pd
from browser import browser
from selenium.webdriver.support.ui import Select

bro = browser()	# Create Webdriver instance
bro.open("https://www.ebay.com/sch/Cars-Trucks/6001/i.html?_from=R40&_nkw=&_in_kw=1&_ex_kw=&_sacat=6001&LH_Sold=1&_udlo=&_udhi=&_samilow=&_samihi=&_sadis=15&_stpos=01923&_sargn=-1%26saslc%3D1&_salic=1&_sop=12&_dmd=1&_ipg=200&LH_Complete=1")	# Go to Ebay page

# Don't redo acquired data
makes_done = sorted(glob.glob(".\\DataBackup\\*.csv"))
makes_dropdown = Select(bro.driver.find_element_by_xpath("//select[@name='Make']"))
makes = makes_dropdown.options[1:]
make_texts = [make.text for make in makes if make.text not in str(makes_done)]

for make in make_texts:
	found = bro.select_make(make)
	if found:
		# Continue where last left off if failure occured
		if os.path.isfile(".\\Data\\" + make.replace('/', '_') + ".pkl"):
			df = pd.read_pickle(".\\Data\\" + make.replace('/', '_') + ".pkl")
		else:
			df = pd.DataFrame()
		
		ads_info = bro.get_ads()
		count = bro.driver.find_element_by_xpath("//span[@class='rcnt']")
		if int(count.text.replace(',', '')) > 200:
			for x in range(int(count.text.replace(',', ''))/200):
				more_button = bro.driver.find_element_by_xpath("//td[@class='pagn-next']")
				more_button.click()
				ads_info.extend(bro.get_ads())

		index = len(ads_info[len(df):])
		for ad in ads_info[len(df):]:
			print index
			index -= 1
			bro.driver.get(ad[2])  # Go to each ad by link
			try:
				cats, vals = bro.get_attrs()
			except:
				print 'Trying Again!!!!'
				bro.wait(60)
				bro.driver.refresh()
				cats, vals = bro.get_attrs()
			cats.extend(["Title", "Price", "Link"])
			vals.extend(ad)
			temp_df = pd.DataFrame([dict(zip(cats,vals))])
			df = df.append(temp_df)
			df.to_pickle(".\\Data\\" + make.replace('/', '_') + ".pkl")
			
		df = df.convert_objects(convert_numeric=True)
		df.to_csv(".\\Data\\" + make.replace('/','_') +'.csv', encoding="utf-8")
		bro.driver.get("https://www.ebay.com/sch/Cars-Trucks/6001/i.html?_from=R40&_nkw=&_in_kw=1&_ex_kw=&_sacat=6001&LH_Sold=1&_udlo=&_udhi=&_samilow=&_samihi=&_sadis=15&_stpos=01923&_sargn=-1%26saslc%3D1&_salic=1&_sop=12&_dmd=1&_ipg=200&LH_Complete=1")
		
		try:
			bro.driver.find_element_by_xpath("//select[@name='Make']")
		except:
			print 'Trying Again 22222 !!!!'
			bro.driver.wait(60)
			bro.driver.refresh()
			bro.driver.get("https://www.ebay.com/sch/Cars-Trucks/6001/i.html?_from=R40&_nkw=&_in_kw=1&_ex_kw=&_sacat=6001&LH_Sold=1&_udlo=&_udhi=&_samilow=&_samihi=&_sadis=15&_stpos=01923&_sargn=-1%26saslc%3D1&_salic=1&_sop=12&_dmd=1&_ipg=200&LH_Complete=1")
		
		bro.driver.find_element_by_xpath("//select[@name='Make']")
		os.remove(".\\Data\\" + make.replace('/', '_') + ".pkl")
bro.driver.close()