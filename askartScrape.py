from bs4 import BeautifulSoup
import requests
import csv
import os.path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import re
import sys
from argparse import ArgumentParser

# Scrape data from askart.com

#### Installation Information ###
# pip install beautifulsoup4
# pip install selenium
# brew install geckodriver

# Append all pieces from page to csv
def appendToCSV(pieceList, outcsv):
	fileExists = os.path.isfile(outcsv)
	headers = ["title", "sales_price", "low_estimate", "high_estimate",
	"signature", "size", "created", "medium", "auction_lot", "auction_house",
	"auction_date"]
	with open(outcsv, "a") as csvfile:
		writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')
		if not fileExists:
			writer.writerow(headers)
		writer.writerows(pieceList)	
	return

# Grab info from each piece
def getPageItems(soup):
	curWork = soup.findAll("div", {"class": "PriceBox"})
	allWork = []
	for piece in curWork:
		items = []
		try:
			items.append(piece.find('b',text='Title:  ').next_sibling.string.strip())
		except:
			items.append(piece.find('b',text='Title:  ').next_sibling.i.contents[0].strip())
		try:
			items.append(piece.find('b',text='Sales Price**:') .next_sibling.string.strip())
		except:
			items.append(piece.find('b',text='Hammer Price*:') .next_sibling.string.strip())
		items.append(piece.find('b',text='Low Estimate:') .next_sibling.string.strip())
		items.append(piece.find('b',text='High Estimate:') .next_sibling.string.strip())
		try:
			items.append(piece.find('b',text='Signature:') .next_sibling.string.strip())
		except:
			items.append("unknown") # Signature information not present
		items.append(piece.find('b',text='Size:  ') .next_sibling.string.strip())
		items.append(piece.find('b',text='Created:') .next_sibling.string.strip())
		items.append(piece.find('b',text='Medium:              ') .next_sibling.string.strip())
		items.append(piece.find('b',text='Auction Lot:') .next_sibling.string.strip())
		items.append(piece.find('a').contents[0])
		items.append(piece.find('b',text='Auction Date:') .next_sibling.string.strip())
		allWork.append(items)
	return allWork

# Append info from each page to csv
def grabArtistPage(page, artistName):
	soup = BeautifulSoup(page,"html.parser")
	page = getPageItems(soup)
	appendToCSV(page, artistName + ".csv")

# Crawl through all artist pages to collect auction info
def grabArtist(startingurl, artistName):
	driver = webdriver.Firefox()
	driver.get(startingurl)
	startingSource = driver.page_source
	startingSoup = BeautifulSoup(startingSource,"html.parser")
	pagestr = startingSoup.find("a", {"class": "last"})['href'] # get last page number
	maxPage = int(re.findall(r'\d+', pagestr)[0])
	page = 1
	while page <= maxPage:
		try:
			sleep(5) # sleep to allow page to load
			htmlSource = driver.page_source
			grabArtistPage(htmlSource, artistName)
			nextPage = driver.find_element_by_class_name('next')
			nextPage.send_keys(Keys.RETURN) 
			print("Page %d of %d scraped" % (page, maxPage))
			page += 1
		except:
			print("Error, crawling stopped!")
			driver.close()
	driver.close()
	print("Done!")

# Run!
if __name__ == "__main__":
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument("-a", "--artist",
					help="name of artist")
	parser.add_argument("-l", "--link",
					help="Link to askart auction records page")
	args = parser.parse_args()
	grabArtist(args.link, args.artist)

###### EXAMPLE ########
# Artist: Ed Ruscha
#pageLink = "http://www.askart.com/auction_records/Ed_Ruscha/30133/Ed_Ruscha.aspx"
#grabArtist(pageLink, "EdRuscha")

