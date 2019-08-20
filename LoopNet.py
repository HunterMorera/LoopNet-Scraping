import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from tkinter import messagebox
import tkinter as tk
from selenium.webdriver.chrome.options import Options
import csv
from mortgage import Loan

# click by path and get elements functions, makes things easier and cleaner below
def clickByPath(path):
    element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, path)))
    element.click();


def getElement(path):
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, path)))
    return element;


def getItems(pageCount):
    for i in range(3,28):
        #variable declerations, url contains pageCount to pull from different pages of the website.
        url = "https://www.loopnet.com/florida_apartment-buildings-for-sale/" + str(pageCount) + "/"
        infoList = [" "]
        price = ""
        units = ""
        grossIncome = ""
        capRate = ""
        ppu = 0
        loanMonthlyPayment = 0
        loanAmmount = 0
        downPayment = 0


        #get title
        title = getElement("//*[@id='Form1']/div[2]/div[5]/div[1]/div[3]/div[" + str(i) + "]/div[2]/a/span").text
        infoList.append(title)

        #get city
        city = getElement("//*[@id='Form1']/div[2]/div[5]/div[1]/div[3]/div[" + str(i) + "]/div[2]/b").text
        infoList.append(city)
        
        #loop through listing details and append them to a list
        table = getElement("//*[@id='Form1']/div[2]/div[5]/div[1]/div[3]/div[" + str(i) + "]/table")
        for row in table.find_elements_by_css_selector('tr'):
            for cell in row.find_elements_by_tag_name('td'):
                infoList.append(cell.text)


        #this block simply cleans up the data we retrieved from the main listing.
        for j in range(len(infoList)):
            currentEntry = infoList[j]

            if("$" in currentEntry):
                price = currentEntry.replace("$","")
                price = price.replace(",","")

            if("Units" in currentEntry):
                units = currentEntry.replace(" Units", "")

            if("%" in currentEntry):
                capRate = currentEntry

        # this is the block where we navigate to the actual listing page in order to get more details on listing
        time.sleep(2)
        hrefValue = getElement("//*[@id='Form1']/div[2]/div[5]/div[1]/div[3]/div[" + str(i) + "]/div[2]/a").get_attribute('href')
        driver.get(hrefValue)
        time.sleep(2)

        # this try catch is attempting to obtain the gross income from the listing, some dont have this section
        # hence the try catch block, so program doesnt crash if no icnome table exists in the listing.
        try:
            tableTwo = driver.find_element_by_css_selector('body > section > main > section > div.module.profile-wrapper > div.row.profile-content-wrapper > div > div > div.column-08.column-ex-large-09.column-large-09.column-medium-09.profile-main-info > div.re-order > section.financial-summary.include-in-page > div > div > table')
            trCount = 0
            tdCount = 0

            for row in tableTwo.find_elements_by_css_selector('tr'):
                for cell in row.find_elements_by_tag_name('td'):
                    if(trCount == 1 and tdCount == 1):
                        grossIncome = cell.text
                    tdCount += 1
                tdCount = 0
                trCount += 1
        except:
            grossIncome = ""

        # this may seem dumb, but I have noticed some listings have the table but have price upon request
        # this just validates that you do in fact have a dollar amount stored here and not text
        if("$" in grossIncome):
            grossIncome = grossIncome
        else:
            grossIncome = ""

        # some listings dont have a number of units so hence the try catch block
        try:
            ppu = float(price) / float(units)
        except:
            ppu = 0
            units = 0

        # here we compute the loan and downpayment ammounts using the mortgage library
        # just a rough calculation you can change these numbers to make more accurate calculations
        try:
            loanAmmount = float(price) * 0.7
            downPayment = float(price) * 0.3
            loan = Loan(principal=loanAmmount, interest=0.058, term=25)
            loanMonthlyPayment = loan.monthly_payment
        except:
            loan = 0
            loanMonthlyPayment = 0
        
        # finally we clear the info list, print and then append all of our listing info to it for writing to CSV
        infoList = [" "]
        if(True):
            print(title)
            print(city)
            print(price)
            print(units)
            print(capRate)
            print("PPU:", ppu)
            print(grossIncome)
            print(loanMonthlyPayment)
            print(downPayment)
            infoList.append(title)
            infoList.append(city)
            infoList.append(price)
            infoList.append(units)
            infoList.append(ppu)
            infoList.append(downPayment)
            infoList.append(loanMonthlyPayment)
            infoList.append(capRate)
            infoList.append(grossIncome)
                

        # finally we append to a file, (doesnt need to be created b4 hand)
        # code will make one if it doesnt exist.
        with open('loopnet.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(infoList)

        # we then navigate back to the listings page to get details on next one in list
        driver.get(url)
        time.sleep(3)

        print("-"*50)


# start up the webdriver and navigate to the loopnet page with all the listings
options = Options()
options.add_argument("--start-fullscreen")
driver = webdriver.Chrome(chrome_options=options)

driver.get('https://www.loopnet.com/florida_apartment-buildings-for-sale/')
time.sleep(5)

# page count needed for web URL navigation
pageCount = 1

# yes this does crash at the end bc I dont know how many pages are available so I just go until it crashes LOL
while(True):
    # this getItems grabs all the details of each listing on the page
    getItems(pageCount)

    # this clicks the next button to goto the next page
    clickByPath("//*[@id='Form1']/div[2]/div[5]/div[1]/div[3]/div[28]/a[2]")
    pageCount += 1





