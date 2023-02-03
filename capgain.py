# http://cgtcalculator.com/
import csv
import datetime
import urllib.request
import json


def ex(date):
    url = 'https://api.exchangerate.host/'+date+'?base=USD&symbols=GBP'
    with urllib.request.urlopen(url) as f:
        print(url + " downloaded")
        r = json.loads(f.read().decode('utf-8'))
        return r["rates"]["GBP"]


date_open = []
quantity_open = []
cost_open = []
with open('View open lots.csv') as open_csv:
    reader = csv.reader(open_csv, delimiter=',')
    for row in reader:
        if (len(row) > 2 and row[1] != "Quantity"):
            d = datetime.datetime.strptime(
                row[0], '%b-%d-%Y').strftime('%d/%m/%Y')
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
            exchange_rate_buy = ex(datetime.datetime.strptime(
                row[0], '%b/%d/%Y').strftime('%Y-%m-%d'))
            date_open.append(do)
            quantity_open.append(row[1])
            cost_open.append(
                (float(row[3])/float(row[1]))*float(exchange_rate_buy))

            # sell
            dc = datetime.datetime.strptime(
                row[2], '%b/%d/%Y').strftime('%d/%m/%Y')
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
