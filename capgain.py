# http://cgtcalculator.com/
import csv
import datetime
import urllib.request
import json
import xml.etree.ElementTree as ET

useHMRC = True

def exchangetoGBP(date):
    if(useHMRC):
        return exHMRC(date.strftime('%m%y'))
    else:
        return ex(date.strftime('%Y-%m-%d'))


def parse_xml(xml):
    """Parse XML file into a list of lists"""
    tree = ET.fromstring(xml)
    for row in tree.findall('exchangeRate'):
        if(row.find('currencyCode').text == 'USD'):
            return row.find('rateNew').text

def ex(date):
    url = 'https://api.exchangerate.host/'+date+'?base=USD&symbols=GBP'
    with urllib.request.urlopen(url) as f:
        print(url + " downloaded")
        r = json.loads(f.read().decode('utf-8'))
        return r["rates"]["GBP"]
    
def exHMRC(date):
    url = 'https://www.hmrc.gov.uk/softwaredevelopers/rates/exrates-monthly-'+date+'.XML'
    try:
        with urllib.request.urlopen(url) as f:
            print(url + " downloaded")
            return parse_xml(f.read().decode('utf-8'))
    except ex:
        print('Error: ' + ex)
        print('HMRC don\'t have data before 2015-01-01, reverting back to daily exchange rates')
        return ex('2015-01-01')

date_open = []
quantity_open = []
cost_open = []
with open('View open lots.csv') as open_csv:
    reader = csv.reader(open_csv, delimiter=',')
    for row in reader:
        if (len(row) > 2 and row[1] != "Quantity"):
            d = datetime.datetime.strptime(
                row[0], '%b-%d-%Y').strftime('%d/%m/%Y')
            
            if(useHMRC):
                exchange_rate = exHMRC(datetime.datetime.strptime(
                    row[0], '%b-%d-%Y'))
            else:
                exchange_rate = ex(datetime.datetime.strptime(
                    row[0], '%b-%d-%Y').strftime('%Y-%m-%d'))

            date_open.append(d)
            quantity_open.append(row[1])
            cost_open.append(float(row[3])*float(exchange_rate))

date_close = []
quantity_close = []
cost_close = []
with open('View closed lots.csv') as open_csv:
    reader = csv.reader(open_csv, delimiter=',')
    for row in reader:
        if (len(row) > 2 and row[1] != "Quantity"):

            # buy
            do = datetime.datetime.strptime(
                row[0], '%b/%d/%Y').strftime('%d/%m/%Y')
            
            if(useHMRC):
                exchange_rate_buy = exHMRC(datetime.datetime.strptime(
                row[0], '%b/%d/%Y').strftime('%m%y'))
            else:
                exchange_rate_buy = ex(datetime.datetime.strptime(
                row[0], '%b/%d/%Y').strftime('%Y-%m-%d'))

            date_open.append(do)
            quantity_open.append(row[1])
            cost_open.append(
                (float(row[3])/float(row[1]))*float(exchange_rate_buy))

            # sell
            dc = datetime.datetime.strptime(row[2], '%b/%d/%Y').strftime('%d/%m/%Y')
            
            if(useHMRC):
                exchange_rate_sell = exHMRC(datetime.datetime.strptime(
                    row[0], '%b/%d/%Y').strftime('%m%y'))
            else:            
                exchange_rate_sell = ex(datetime.datetime.strptime(
                    row[2], '%b/%d/%Y').strftime('%Y-%m-%d'))
                                
            date_close.append(dc)
            quantity_close.append(row[1])
            cost = float(row[3])/float(row[1])
            cost_close.append(cost*float(exchange_rate_sell))

with open('cgt.tsv', 'w', newline='',) as csvfile:
    fieldnames = ['Action', 'Date', 'Stock_Name',
                  'Quantity', 'price', 'brokercost', 'tax']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
    for t in range(0, len(date_open)):
        writer.writerow({'Action': 'B', 'Date': date_open[t], 'Stock_Name': 'MSFT',
                        'Quantity': quantity_open[t], 'price': cost_open[t], 'brokercost': '0', 'tax': '0'})

    for c in range(0, len(date_close)):
        writer.writerow({'Action': 'S', 'Date': date_close[c], 'Stock_Name': 'MSFT',
                        'Quantity': quantity_close[c], 'price': cost_close[c], 'brokercost': '0', 'tax': '0'})
