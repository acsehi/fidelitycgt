# http://cgtcalculator.com/
import csv
import datetime
import urllib.request
import json
import xml.etree.ElementTree as ET

accessKey=""

exchangeTraded = True
use_HMRC_exchange_rates = True

def exchangetoGBP(date):
    if(not(exchangeTraded)):
        return 1.0
    if (use_HMRC_exchange_rates):
        try:
            return exchangeHMRC(date.strftime('%m%y'))
        except Exception as ex:
            if (ex.code == 404):
                print('HMRC don\'t have data before 2015-01-01, reverting back to daily exchange rates')
                return exchange(date.strftime('%Y-%m-%d'))
            else:
                raise ex
    else:
        return exchange(date.strftime('%Y-%m-%d'))

def parse_xml(xml):
    """Parse XML file into a list of lists"""
    tree = ET.fromstring(xml)
    for row in tree.findall('exchangeRate'):
        if (row.find('currencyCode').text == 'USD'):
            return row.find('rateNew').text

def exchange(date):
    url = 'https://api.exchangerate.host/'+date+'?base=USD&symbols=GBP&access_key='+accessKey
    with urllib.request.urlopen(url) as f:
        r = json.loads(f.read().decode('utf-8'))
        exchange_rate = r["rates"]["GBP"]
        print(url + " downloaded, exchange rate: " + str(exchange_rate))

        return exchange_rate

def exchangeHMRC(date):
    url = 'https://www.hmrc.gov.uk/softwaredevelopers/rates/exrates-monthly-'+date+'.XML'
    with urllib.request.urlopen(url) as f:
        exchange_rate = 1.0/float(parse_xml(f.read().decode('utf-8')))
        print(url + " downloaded, exchange rate: " + str(exchange_rate))
        return exchange_rate

def validateCurrency(row):
    if (row[0] == "The values are displayed in GBP"):
        raise Exception("Please download history in USD")

date_open = []
quantity_open = []
value_open = []
with open('View open lots.csv') as open_csv:
    reader = csv.reader(open_csv, delimiter=',')
    for row in reader:
        if (len(row) > 2 and row[1] != "Quantity"):
            d = datetime.datetime.strptime(
                row[0], '%b-%d-%Y').strftime('%d/%m/%Y')
            exchange_rate = exchangetoGBP(
                datetime.datetime.strptime(row[0], '%b-%d-%Y'))
            date_open.append(d)
            quantity_open.append(row[1])
            value_open.append(float(row[3])*float(exchange_rate))
        else:
            validateCurrency(row)

date_close = []
quantity_close = []
cost_close = []
with open('View closed lots.csv') as open_csv:
    # Row schema: Date acquired,Quantity,Date sold or transferred,Proceeds,Cost basis,Gain/loss,Term
    reader = csv.reader(open_csv, delimiter=',')
    for row in reader:
        if (len(row) > 2 and row[1] != "Quantity"):            
            # buy
            quantity = float(row[1])
            buy_date = row[0]
            do = datetime.datetime.strptime(
                buy_date, '%b/%d/%Y').strftime('%d/%m/%Y')

            exchange_rate_buy = exchangetoGBP(
                datetime.datetime.strptime(buy_date, '%b/%d/%Y'))

            date_open.append(do)
            quantity_open.append(quantity)
            cost_basis = row[4]
            value_open.append(
                (float(cost_basis)/float(quantity))*float(exchange_rate_buy))

            # sell
            sell_date = row[2]
            dc = datetime.datetime.strptime(
                sell_date, '%b/%d/%Y').strftime('%d/%m/%Y')
            exchange_rate_sell = exchangetoGBP(
                datetime.datetime.strptime(sell_date, '%b/%d/%Y'))

            date_close.append(dc)
            quantity_close.append(quantity)
            proceeds = row[3]
            cost = float(proceeds)/float(quantity)
            cost_close.append(cost*float(exchange_rate_sell))
        else:
            validateCurrency(row)

with open('cgt.tsv', 'w', newline='',) as csvfile:
    fieldnames = ['Action', 'Date', 'Stock_Name',
                  'Quantity', 'price', 'brokercost', 'tax']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
    for t in range(0, len(date_open)):
        writer.writerow({'Action': 'B', 'Date': date_open[t], 'Stock_Name': 'MSFT',
                        'Quantity': quantity_open[t], 'price': value_open[t], 'brokercost': '0', 'tax': '0'})

    for c in range(0, len(date_close)):
        writer.writerow({'Action': 'S', 'Date': date_close[c], 'Stock_Name': 'MSFT',
                        'Quantity': quantity_close[c], 'price': cost_close[c], 'brokercost': '0', 'tax': '0'})
