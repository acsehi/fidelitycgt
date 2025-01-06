# http://cgtcalculator.com/
import csv
import datetime
import urllib.request
import json
import xml.etree.ElementTree as ET


trial_base64 = "c36cefa5b34520b268302b35c738e5ba"

use_exchange = True
use_HMRC_exchange_rates = True


def convert_to_gbp(date, exchange_rate_cache):
    if (not (use_exchange)):
        return 1.0
    if (use_HMRC_exchange_rates):
        try:
            return exchange_HMRC(date.strftime('%Y-%m'), exchange_rate_cache)
        except Exception as ex:
            if (ex.code == 404):
                print(
                    'HMRC don\'t have data before 2015-01-01, reverting back to daily exchange rates')
                return exchange(date.strftime('%Y-%m-%d'), exchange_rate_cache)
            else:
                raise ex
    else:
        return exchange(date.strftime('%Y-%m-%d'), exchange_rate_cache)


def parse_xml(xml):
    """Parse XML file into a list of lists"""
    tree = ET.fromstring(xml)
    for row in tree.findall('exchangeRate'):
        if (row.find('currencyCode').text == 'USD'):
            return row.find('rateNew').text


def exchange(date, exchange_rate_cache):
    if (date in exchange_rate_cache):
        print("Using cached exchange rate for " + date)
        return exchange_rate_cache[date]
    url = 'http://api.exchangerate.host/convert?access_key=' + \
        trial_base64+'&from=USD&to=GBP&amount=1&date=' + date
    
    with urllib.request.urlopen(url) as f:
        r = json.loads(f.read().decode('utf-8'))
        exchange_rate = r["result"]
        exchange_rate_cache[date] = exchange_rate
        print(url + " downloaded, exchange rate: " + str(exchange_rate))

        return exchange_rate


def exchange_HMRC(date, exchange_rate_cache):
    if (date in exchange_rate_cache):
        print("Using cached exchange rate for " + date)
        return exchange_rate_cache[date]
    
    url = 'https://www.trade-tariff.service.gov.uk/api/v2/exchange_rates/files/monthly_xml_'+date+'.xml'
    
    with urllib.request.urlopen(url) as f:
        exchange_rate = 1.0/float(parse_xml(f.read().decode('utf-8')))
        exchange_rate_cache[date] = exchange_rate
        print(url + " downloaded, exchange rate: " + str(exchange_rate))
        return exchange_rate


def save_exchange_rates(exchange_rate_cache_file, exchange_rate_cache):
    with open(exchange_rate_cache_file, 'w') as fp:
        json.dump(exchange_rate_cache, fp)


def load_exchange_rates(exchange_rate_cache_file):
    try:
        with open(exchange_rate_cache_file) as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {}


def validate_currency(row):
    if (row[0] == "The values are displayed in GBP"):
        raise Exception("Please download history in USD")

def run(open_lots_file, closed_lots_file, output_file, exchange_rate_cache_file):
    date_open = []
    quantity_open = []
    value_open = []
    exchange_rate_cache = load_exchange_rates(exchange_rate_cache_file)
    with open(open_lots_file) as open_csv:
        reader = csv.reader(open_csv, delimiter=',')
        for row in reader:
            if (len(row) > 2 and row[1] != "Quantity"):
                d = datetime.datetime.strptime(
                    row[0], '%b-%d-%Y').strftime('%d/%m/%Y')
                exchange_rate = convert_to_gbp(
                    datetime.datetime.strptime(row[0], '%b-%d-%Y'), exchange_rate_cache)
                date_open.append(d)
                quantity_open.append(row[1])
                value_open.append(float(row[3])*float(exchange_rate))
            else:
                validate_currency(row)

    date_close = []
    quantity_close = []
    cost_close = []
    with open(closed_lots_file) as open_csv:
        # Row schema: Date acquired,Quantity,Date sold or transferred,Proceeds,Cost basis,Gain/loss,Term
        reader = csv.reader(open_csv, delimiter=',')
        for row in reader:
            if (len(row) > 2 and row[1] != "Quantity"):
                # buy
                quantity = float(row[1])
                buy_date = row[0]
                do = datetime.datetime.strptime(
                    buy_date, '%b/%d/%Y').strftime('%d/%m/%Y')

                exchange_rate_buy = convert_to_gbp(
                    datetime.datetime.strptime(buy_date, '%b/%d/%Y'), exchange_rate_cache)

                date_open.append(do)
                quantity_open.append(quantity)
                cost_basis = row[4]
                value_open.append(
                    (float(cost_basis)/float(quantity))*float(exchange_rate_buy))

                # sell
                sell_date = row[2]
                dc = datetime.datetime.strptime(
                    sell_date, '%b/%d/%Y').strftime('%d/%m/%Y')
                exchange_rate_sell = convert_to_gbp(
                    datetime.datetime.strptime(sell_date, '%b/%d/%Y'), exchange_rate_cache)

                date_close.append(dc)
                quantity_close.append(quantity)
                proceeds = row[3]
                cost = float(proceeds)/float(quantity)
                cost_close.append(cost*float(exchange_rate_sell))
            else:
                validate_currency(row)

    with open(output_file, 'w', newline='',) as csvfile:
        fieldnames = ['Action', 'Date', 'Stock_Name',
                      'Quantity', 'price', 'brokercost', 'tax']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
        for t in range(0, len(date_open)):
            writer.writerow({'Action': 'B', 'Date': date_open[t], 'Stock_Name': 'MSFT',
                            'Quantity': quantity_open[t], 'price': value_open[t], 'brokercost': '0', 'tax': '0'})

        for c in range(0, len(date_close)):
            writer.writerow({'Action': 'S', 'Date': date_close[c], 'Stock_Name': 'MSFT',
                            'Quantity': quantity_close[c], 'price': cost_close[c], 'brokercost': '0', 'tax': '0'})

    save_exchange_rates(exchange_rate_cache_file, exchange_rate_cache)
