from congress import Congress
from bs4 import BeautifulSoup
from urllib import request
from time import process_time
import csv
import xlsxwriter as excel
import sys
#GLOBALS
#ProPublica Congressional API Key
key = "5RnLVh2UJXE6htQSMktG8MsXbEkYeLXmLXwns9FJ"
#Number of the current congress. E.G. "Nancy Pelosi is the speaker of the house
#for the 117th congress"
congressNum = "117"
#Hexadecimal Congressional Member ID (found in congressional bio URL on congress.gov)
memberID = "F000466"
#Member name information
memberLastName = "Fitzpatrick"
memberFirstName = "Brian"
#Sets global variable to store ProPublica Congressional API session
congress = Congress(key)
#Header to allow access to scrape congress.gov. DO NOT ALTER
header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
      'AppleWebKit/537.11 (KHTML, like Gecko) '
      'Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}

#Fetches the total number of pages of results for sponsored and cosponsored bills
#RETURN: integer, used to scroll congress.gov in soupify()
def getNumPages():
    #Creates and sends the HTTP request using a formatted string based on global variables above
    req = request.Request(f"https://www.congress.gov/member/{memberFirstName}-{memberLastName}/{memberID}?s=1&r=7&q=%7B%22congress%22%3A%22{congressNum}%22%2C%22type%22%3A%22bills%22%7D&pageSize=100&page=1", None, headers=header)
    #Opens and reads the HTML text of the website
    openReq = request.urlopen(req).read()
    #Uses BeautifulSoup4 to classify and organize HTML code to be more easily searchable
    soup = BeautifulSoup(openReq, "lxml")
    #On single-page entries, the span "results-number" will not appear. Thus, if it does
    #exist, the program finds the number of pages and returns it. Otherwise, the returned
    #page number is 1
    try:
        #TODO fix text indexing to handle multi-digit numbers of pages
        return int(soup.find_all("span", class_="results-number")[1].text[4])
    except:
        return 1

#Fetches all pages of results and systematically scrapes out the bill information
#RETURN: list of BS4 objects that can then be further sorted in formatResults()
def soupify():
    #Sets empty list to collect results
    results = []
    #Fetches number of pages of results
    numPages = getNumPages()
    #Normally, would not use if/else here, but URL has to be specially formatted for single-page entries
    if numPages > 1:
        #Scrolls every page
        for i in range(1, numPages + 1):
            #Accesses the current page number
            stock = request.Request(f"https://www.congress.gov/member/{memberFirstName}-{memberLastName}/{memberID}?s=1&r=7&q=%7B%22congress%22%3A%22{congressNum}%22%2C%22type%22%3A%22bills%22%7D&pageSize=100&page={i}", None, headers=header)
            #Opens and reads current page
            seasoning = request.urlopen(stock).read()
            #Uses BeautifulSoup4 to classify and organize HTML code to be more easily searchable
            soup = BeautifulSoup(seasoning, "lxml")
            #Adds list of class "expanded" divs (bill information results) to results list
            results.extend(soup.find_all("li", class_="expanded"))
    else:
        #Repeats above process, but only once for the single page
        stock = request.Request(f"https://www.congress.gov/member/{memberFirstName}-{memberLastName}/{memberID}?s=1&r=7&q=%7B%22congress%22%3A%22{congressNum}%22%2C%22type%22%3A%22bills%22%7D", None, headers=header)
        specialSauce = request.urlopen(stock).read()
        soup = BeautifulSoup(specialSauce, "lxml")
        results.extend(soup.find_all("li", class_="expanded"))
    return results

#Takes "soup" of result objects from BS4 and packages them into
#a list of dictionaries
#RETURN: a list of dictionaries
def formatResults():
    #Gets the result "soup" fetched from congress.gov
    resultSoup = soupify()
    #Sets up an empty list to collect the dictionaries of results
    resultDicts = []
    for result in resultSoup:
        #Collects bill title, HR number, sponsor, and committee into variables
        title = (result.find("span", class_="result-title").text)
        HRNum = result.find("span", class_="result-heading").find("a").text
        sponsor = result.find_all("span", class_="result-item")[0].find("a").text
        committee = result.find_all("span", class_="result-item")[1].text.split("|")[0].split(";")[0]
        committee = committee[21:len(committee)]
        #Packages these variables into a dictionary
        resultDicts.append({"HRNum" : HRNum,
                           "Title" : title,
                           "Sponsor" : sponsor,
                           "Committee" : committee})
    return resultDicts

#Takes neatly dictionary'd data and places it in a Microsoft Excel format.
#Recommended for sheet manipulation and distribution
#RETURN: void
def packageResultsExcel():
    #Calls formatResults() to retrieve a list of dictionaries formatted from the BeautifulSoup webscrape
    resultDicts = formatResults()
    #Creates a custom-named workbook and sheet and overrides any older workbooks in the directory
    book = excel.Workbook(f"{memberLastName} Bill Sheet {congressNum}.xlsx")
    sheet = book.add_worksheet()
    #Sets headings (NOT OPTIMIZED)
    sheet.write(0, 0, "HRNum")
    sheet.write(0, 1, "Title")
    sheet.write(0, 2, "Sponsor")
    sheet.write(0, 3, "Committee")
    #Sets starting point on second row to not overwrite the heading (rows and columns are indexed from 0)
    row = 1
    #Copies data from the result dictionaries (NOT OPTIMIZED)
    for dict in resultDicts:
        sheet.write(row, 0, dict["HRNum"])
        sheet.write(row, 1, dict["Title"])
        sheet.write(row, 2, dict["Sponsor"])
        sheet.write(row, 3, dict["Committee"])
        #Moves copier to next row
        row += 1
    #Saves and closes the workbook
    book.close()

#Does the same as above, but into a more machine-readable CSV file. Encoded in UTF-8,
#but you will encounter glyphs when trying to preview in Excel.
#RETURN: void
def packageResultsCSV():
    #Pulls list of result dictionaries from formatResults()
    resultDicts = formatResults()
    #Sets custom CSV name and creates the document
    with open(f"{memberLastName} Bill Sheet {congressNum}.csv", mode="w", encoding="utf-8") as sheet:
        #Sets column names
        fieldnames = ["HRNum", "Title", "Sponsor", "Committee"]
        #Establishes a dictionary-based writer that reads from the field names in resultDicts
        writer = csv.DictWriter(sheet, fieldnames=fieldnames)
        #Writes column names
        writer.writeheader()
        #Scrolls every dict in resultDicts
        for dict in resultDicts:
            #Copies the dict into a new row in the CSV
            writer.writerow(dict)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    t1 = process_time()
    packageResultsExcel()
    t2 = process_time()
    t = t2-t1
    print(str(t) + "s")
