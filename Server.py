from urllib.request import Request,urlopen
from datetime import *
import time
from bs4 import BeautifulSoup
import sqlite3
from decimal import Decimal
from re import sub
from flask import Flask,jsonify,request as frequest,abort
from statistics import mean, variance

app = Flask(__name__)
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
        CREATE TABLE gold(
            date TEXT PRIMARY KEY,
            price DECIMAL
        );
    """
    cursor.execute(sql_command)
    sql_command = """
        CREATE TABLE silver(
            date TEXT PRIMARY KEY,
            price DECIMAL
        );
    """
    cursor.execute(sql_command)

    #Save changes and exit
    connection.commit()
    connection.close()

#Scrape a url
def Scrape(url,table):
    #Fetch the url and turn into something parsable
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resource = urlopen(req).read()
    soup = BeautifulSoup(resource, 'html.parser')

    #Find all the rows with data in them
    rows = soup.find(class_ = 'historicalTbl').find_all('tr')
    connection = sqlite3.connect("resource.db")
    cursor = connection.cursor()

    for row in rows:
        #First column is always date
        date = row.find_next('td')
        #Next column is always price
        price = date.find_next_sibling('td')

        #values are stored un the data-real-value attribute

        #date in and converted to a string in Iso format
        date = int(date['data-real-value'])
        date = datetime.utcfromtimestamp(date);
        date = date.strftime("%Y-%m-%d")

        #Conver price to a decimal
        price = price['data-real-value']
        price = float(sub(r'[^\d.]', '', price))

        #Replace will replace any duplicate entries with the most recent one
        sql_command ="REPLACE into "+table+"(date,price) Values(?,?) "

        cursor.execute(sql_command,(date,price))

    connection.commit()
    connection.close()

@app.route("/commodity",methods=['GET'])
def commodities():
    start = frequest.args.get('start_date',type=str)
    end = frequest.args.get('end_date')
    commodity_type = frequest.args.get('commodity_type').lower()


    #Handle some common errors with custom messages
    if(start == None):
        abort(400, 'No start_date specified')
    if(end == None):
        abort(400, 'No end_date specified')
    if(commodity_type == None):
        abort(400, 'No commodity_type specified')

    responce = {"data":{},"mean":None,"variance":None}
    #wrap our sql request in a try catch to report all other errors

    #Store a list of prices for statistics later to use the python statistics library
    #in theory the way these functions are implemented should account for floating point error
    price_list = [];
    try:
        connection = sqlite3.connect("resource.db")
        cursor = connection.cursor()
        sql_command = "SELECT date AS day,price FROM "+ str(commodity_type) +" WHERE date(day) >= date(?) AND date(day) <= date(?);"
        cursor.execute(sql_command,(start,end))
        cursor.fetchall
        for result in cursor:
            responce["data"].update({result[0]:result[1]})
            price_list.append(result[1])
        connection.commit()
        connection.close()
    except Exception as e:
        abort(400,e)

    #custom or numpy base stats is faster but less accurate
    responce["mean"] = mean(price_list)
    responce["variance"] = variance(price_list)
    

    return jsonify(responce);

Setup()
Scrape('https://www.investing.com/commodities/gold-historical-data','gold')
Scrape('https://www.investing.com/commodities/silver-historical-data','silver')

#Run our server on port 8080
if __name__ == '__main__':
    app.run(port=8080)
