import time
from lib.Pages.AutoTempest import AutoTempest

page = AutoTempest()

page.bro.click_button("//form[@id='search-main']//button[@type='submit']")  # Submit Button
time.sleep(1) # Obnoxious but page closes if this isn't here
page.bro.click_button("//button[@class='change-sources show-box']")  # Sources Button
page.bro.click_button("//span[@class='checkboxWrap eba mash']")  # Ebay Auctions Button
page.bro.click_button("//button[@class='update-results']")  # Update Button

ads_info = []
ads = page.get_ads()
for ad in ads:
	print len(ads) - len(ads_info)  # Some indication of progress
	title = page.bro.get_element_text(".//div[@class='description-wrap']//h2//a", parent=ad)  # Ad Title
	link = page.bro.get_element_attribute(".//div[@class='description-wrap']//h2//a", "href", parent=ad)  # Ad Link
	
	year = page.get_year(title)  # Get year from title text
	
	price = page.bro.get_element_text(".//div[@class='price']", parent=ad)  # Ad Price
	mileage = page.bro.get_element_text(".//span[@class='info mileage']", parent=ad)  # Ad Mileage
	
	ad_info = {"Title":title, "Year":year, "Mileage":mileage, "Price":price, "Link":link}
	ads_info.append(ad_info)  # Keep track of all Ad Information

page.bro.driver.close()

# Save data to csv file
page.write_to_csv("AutoTempest", ads_info)