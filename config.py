"""Configuration settings for the Fidelity CGT Calculator."""

import os
from typing import Optional


class Config:
    """Configuration class for the CGT calculator."""
    
    # Exchange rate settings
    USE_HMRC_RATES: bool = True
    
    # Note: This is a free-tier API key for exchangerate.host
    # Users can override with their own key via EXCHANGE_RATE_API_KEY environment variable
    # The API key is used as fallback when HMRC data is unavailable (pre-2015)
    EXCHANGE_RATE_API_KEY: str = os.getenv(
        'EXCHANGE_RATE_API_KEY',
        'c36cefa5b34520b268302b35c738e5ba'  # Free tier API key (fallback only)
    )
    
    # Stock symbol
    STOCK_NAME: str = 'MSFT'
    
    # Default file paths
    DEFAULT_OPEN_LOTS_FILE: str = 'View open lots.csv'
    DEFAULT_CLOSED_LOTS_FILE: str = 'View closed lots.csv'
    DEFAULT_OUTPUT_FILE: str = 'cgt.tsv'
    DEFAULT_CACHE_FILE: str = 'exchange_rate_cache.json'
    
    # API endpoints
    HMRC_API_URL: str = "https://www.trade-tariff.service.gov.uk/api/v2/exchange_rates/files/monthly_xml_{date}.xml"
    EXCHANGE_HOST_API_URL: str = "http://api.exchangerate.host/convert?access_key={api_key}&from=USD&to=GBP&amount=1&date={date}"
    
    # Expected currency for input files
    EXPECTED_CURRENCY: str = "USD"
