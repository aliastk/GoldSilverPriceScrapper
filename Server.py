from urllib.request import Request,urlopen
import time
from bs4 import BeautifulSoup
import sqlite3

#Scrape a url
def Scrape(url):
    #Fetch the url and turn into something parsable
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resource = urlopen(req).read()
    soup = BeautifulSoup(resource, 'html.parser')

    #Find all the rows with data in them
    rows = soup.find(class_ = 'historicalTbl').find_all('tr')
    for row in rows:
        #First column is always date
        date = row.find_next('td')
        #Next column is always price
        price = date.find_next_sibling('td')

        #values are stored un the data-real-value attribute

        #date is read as an epoch time stamp needs to be formatted
        print(date['data-real-value'])
        print(price['data-real-value'])
        print("")

#setup the database
def Setup():
    connection = sqlite3.connect("resource.db")
    cursor = connection.cursor()

    #Drop existing tables
    sql_command = """
        DROP TABLE IF EXISTS Gold;
    """
    cursor.execute(sql_command)
    sql_command = """
        DROP TABLE IF EXISTS Silver;
    """
    cursor.execute(sql_command)

    #Create tables
    sql_command = """
        CREATE TABLE Gold(
            date Date,
            price decimal
        );
    """
    cursor.execute(sql_command)

    #Save changes and exit
    connection.commit()
    connection.close()

Setup()
print("Gold")
Scrape('https://www.investing.com/commodities/gold-historical-data')
print("Silver")
Scrape('https://www.investing.com/commodities/silver-historical-data')
