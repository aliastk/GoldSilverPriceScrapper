# GoldSilverPriceScrapper

Scrapes gold and silver prices from investing.com.

Installation:
pip install -r requirements.txt

To Run:
py Server.py

Example API Call:curl 'http://127.0.0.1:8080/commodity?start_date=2019-05-14&end_date=2019-06-07&commodity_type=silver'

Notes:
Prioritizes accuracy over speed. Both mean and variance use a slower more accurate algorithm then numpy
In general I tried to avoid dependencies outside of python packages hence sqlite, this makes installation faster for
the reviewer. However note that sqlite lacks a DATE type and the VAR (variance) function.

Alternative Schema: 
CREATE TABLE Commodity(
            type TEXT
            date DATE PRIMARY KEY,
            price DECIMAL
            PRIMARY KEY(type,date)
);
