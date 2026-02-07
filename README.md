# Fidelity UK Capital tax gain calculator for MSFT employees
Calculate your capital tax gain from MSFT shares from your Fidelity account using http://cgtcalculator.com/. This tool will convert your fidelity transaction export to format readable by http://cgtcalculator.com/. Trades are converted back to GBP on historical rates. All outputs are in GBP.

## Recent Improvements

The codebase has been refactored with:
- ✨ Better code organization with separate modules for different concerns
- 📝 Type hints throughout for better IDE support
- 🧪 Improved test coverage and error handling
- 📚 Comprehensive documentation
- ⚙️ Centralized configuration management

See [ARCHITECTURE.md](ARCHITECTURE.md) for details on the code structure.

## ESPP
If you bought ESPP stocks, their Fair Market Value will be used. This will overestimate your gains by 11% for ESPP shares. You can manually fix this in the output, our you can just accept that your reported capital gains are 0-10% less than what was calculated.

## Instructions
1. Login to fideliy and navigate to https://netbenefitsww.fidelity.com/mybenefitsww/stockplans/navigation/PositionSummary#/
2. Select "View share details" for your MSFT stocks
3. Select "Asset currency" to show transactions in USD
4. Export data from "Current shares" and "Previously held shares" tabs. Make sure both are in USD. Files are:
    - "View closed lots.csv"
    - "View open lots.csv"
6. Save the files next to capgain.py and run `python capgain.py` from a command prompt
    - If you don't have python installed, download it first from: https://www.python.org/downloads/
    - Requires Python 3.12 or higher
7. Upload the generated 'cgt.tsv' to http://cgtcalculator.com/ which will calculate the gain in each tax year

If you want to simulate a hypotetical sell transaction, just copy-paste an existing sale transaction, and change the parameters to your planed sale.

## Configuration

You can customize the behavior by setting environment variables:
- `EXCHANGE_RATE_API_KEY`: Your API key for exchangerate.host (optional, has a free-tier default)
  - The included API key is for the free tier and only used as a fallback when HMRC data is unavailable (pre-2015)
  - HMRC rates are preferred and used by default for all transactions from 2015 onwards

See [config.py](config.py) for all configuration options.

## Development

### Running Tests

```bash
python TestCapGaintest.py
```

### Code Structure

- `capgain.py`: Simple entry point
- `calculator.py`: Main calculation logic
- `exchange_rate_service.py`: Exchange rate fetching and caching
- `csv_parser.py`: Fidelity CSV file parsing
- `models.py`: Data models
- `config.py`: Configuration settings

## Disclaimer
Although this tool has been tested comprehensively the owners of this tool accept no responsibility for any errors.
