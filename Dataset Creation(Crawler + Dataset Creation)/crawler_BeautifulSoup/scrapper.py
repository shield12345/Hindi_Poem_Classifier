# File for web crawling hindwi site
# import libraries
from bs4 import BeautifulSoup
import requests
import json
import pickle

# Links to crawl
links = [
"/poets?startswith=अ",
"/poets?startswith=आ", 
"/poets?startswith=इ",
"/poets?startswith=ई",
"/poets?startswith=उ",
"/poets?startswith=ऋ",
"/poets?startswith=ए",
"/poets?startswith=ओ",
"/poets?startswith=क",
"/poets?startswith=ख",
"/poets?startswith=ग",
"/poets?startswith=घ",
"/poets?startswith=च",
"/poets?startswith=छ",
"/poets?startswith=ज",
"/poets?startswith=ट",
"/poets?startswith=ठ",
"/poets?startswith=ड",
"/poets?startswith=त",
"/poets?startswith=द",
"/poets?startswith=ध",
"/poets?startswith=न",
"/poets?startswith=प",
"/poets?startswith=फ",
"/poets?startswith=फ़",
"/poets?startswith=ब",
"/poets?startswith=भ",
"/poets?startswith=म",
"/poets?startswith=य",
"/poets?startswith=र",
"/poets?startswith=ल",
"/poets?startswith=व",
"/poets?startswith=श",
"/poets?startswith=स",
"/poets?startswith=ह",
]

# Variables to store the poets and poems count
poets_count = 0
poems_count = 0

final_output = []

# Iterate through all the links
for mainLink in links:
	page = requests.get("https://www.hindwi.org" + mainLink)
	print(mainLink)
	soup = BeautifulSoup(page.content, features="lxml")
	# Extract the division with the class "nmPoetListingItem"
	mainDivs = soup.find_all('div',class_="nwPoetListingItem")
	# Iterate through all the found divisions
	for division in mainDivs:
		# Extract the name of the poet
		name = division.find_all('h2')[0].get_text()
		print(name)
		# Extract the preiod in which the poet was active if provided
		dateSpan = division.find_all('span',class_="poetListDate")
		date = ""
		if (len(dateSpan)>0):
			date = dateSpan[0].get_text()
		# Increment the poets count
		poets_count = poets_count + 1
		# print(name,date,link)

		# Find all the different types of poems written and iterate over them
		DiffLinks = division.find_all('a',class_="ptContentTyp")
		for link in DiffLinks:
			# poemsPage = requests.get(link.get('href'))
			# print(link.get('href'))
			# print(link.get_text(),"\n")
			str = link.get_text()

			val = str.split()
			v = ' '.join(val[1:])
			# In case of the following elements we dont include them in the set, because they arent poems
			if v in ['उद्धरण', 'पहेलियाँ', 'ई-पुस्तक', 'अड़िल्ल']:
				continue

			# Open the poems page and parse it
			poemsPage = requests.get(link.get('href'))
			soupPoems = BeautifulSoup(poemsPage.content, features="lxml")

			# For all the doha's we have to do them separately
			if v in ['दोहा']:
				doheDivs = soupPoems.find_all('div',class_="sherLines")
				# Find all the dohes
				for doheDiv in doheDivs:
					# Increment the poems count
					poems_count = poems_count + 1
					paras = doheDiv.find_all('div',class_="c")[0].find_all('p')
					poem = ""
					lineno = 0
					for p in paras:
						if lineno > 0:
							poem += '\n'
						poem += p.get_text()
						lineno = lineno + 1
					# Store the output
					final_output.append([name,date,v,"",poem])
				
			else:
				# Find the poems divisions
				poemsDivs = soupPoems.find_all('div',class_="contentListItems")

				for poemDiv in poemsDivs:
					poemAnchor = poemDiv.find_all('a')[1]
					poemName = poemAnchor.find_all('h3')[0].get_text()
					poemLink = poemAnchor.get('href')
					poems_count = poems_count + 1
					# Open the poem link
					poemPage = requests.get(poemLink)
					soupPoem = BeautifulSoup(poemPage.content, features="lxml")

					allDivsT = soupPoem.find_all('div',class_="poemPageContentBody")
					if len(allDivsT) == 0:
						print(poemLink)
						continue
					allDivs = allDivsT[0]
					paras = allDivs.find_all('p')
					poem = ""
					lineno = 0
					# Read each line of the poem and concantenate
					for p in paras:
						if lineno > 0:
							poem += '\n'
						poem += p.get_text()
						lineno = lineno + 1
					# append the result to the final output list
					final_output.append([name,date,v,poemName,poem])

# Print statistics
print("Number of Poets:- ", poets_count)
print("Number of Poems:- ", poems_count)

# Store the files using json and pickle
with open("poems.json", "w") as outfile: 
	json.dump(final_output, outfile) 

with open('poems.obj', 'wb') as fp:
	pickle.dump(final_output, fp)
