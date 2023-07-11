# Fidelity UK Capital tax gain calculator for MSFT employees
Calculate your capital tax gain from MSFT shares from your Fidelity account using http://cgtcalculator.com/. This tool will convert your fidelity transaction export to format readable by http://cgtcalculator.com/. Trades are converted back to GBP on historical rates. All outputs are in GBP.

## Instructions
1. Login to fideliy and navigate to https://netbenefitsww.fidelity.com/mybenefitsww/stockplans/navigation/PositionSummary#/
2. Select "View share details" for your MSFT stocks
3. Select "Asset currency" to show transactions in USD
4. Export data from "Current shares" and "Previously held shares" tabs. Make sure both are in USD. Files are:
    - "View closed lots.csv"
    - "View open lots.csv"
6. Save the files next to capgain.py and run `python capgain.py` from a command prompt
    - If you don't have python installed, download it first from: https://www.python.org/downloads/
7. Upload the generated 'cgt.tsv' to http://cgtcalculator.com/ which will calculate the gain in each tax year

If you want to simulate a hypotetical sell transaction, just copy-paste an existing sale transaction, and change the parameters to your planed sale.

## Disclaimer
Although this tool has been tested comprehensively the owners of this tool accept no responsibility for any errors.
