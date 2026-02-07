"""Exchange rate service for converting USD to GBP using HMRC and alternative APIs."""

import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Optional
from urllib.error import HTTPError, URLError

from config import Config


class ExchangeRateService:
    """Service for fetching and caching exchange rates from various sources."""

    def __init__(self, cache_file: str, use_hmrc: bool = True):
        """
        Initialize the exchange rate service.
        
        Args:
            cache_file: Path to the JSON file for caching exchange rates
            use_hmrc: Whether to prefer HMRC rates (True) or daily rates (False)
        """
        self.cache_file = cache_file
        self.use_hmrc = use_hmrc
        self.cache: Dict[str, float] = self._load_cache()

    def _load_cache(self) -> Dict[str, float]:
        """Load exchange rate cache from file."""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_cache(self) -> None:
        """Save exchange rate cache to file."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def get_exchange_rate(self, date: datetime) -> float:
        """
        Get USD to GBP exchange rate for a given date.
        
        Args:
            date: The date for which to get the exchange rate
            
        Returns:
            The exchange rate from USD to GBP
            
        Raises:
            URLError: If the API request fails
        """
        if self.use_hmrc:
            try:
                return self._get_hmrc_rate(date)
            except (HTTPError, URLError) as ex:
                # HMRC doesn't have data before 2015-01-01
                if isinstance(ex, HTTPError) and ex.code == 404:
                    print(f"HMRC data unavailable for {date.strftime('%Y-%m')}, using daily exchange rates")
                    return self._get_daily_rate(date)
                raise
        else:
            return self._get_daily_rate(date)

    def _get_hmrc_rate(self, date: datetime) -> float:
        """
        Get HMRC monthly exchange rate.
        
        Args:
            date: The date for which to get the exchange rate
            
        Returns:
            The exchange rate from USD to GBP
        """
        date_key = date.strftime('%Y-%m')
        
        if date_key in self.cache:
            print(f"Using cached HMRC exchange rate for {date_key}")
            return self.cache[date_key]
        
        url = Config.HMRC_API_URL.format(date=date_key)
        
        try:
            with urllib.request.urlopen(url) as response:
                xml_data = response.read().decode('utf-8')
                exchange_rate = self._parse_hmrc_xml(xml_data)
                self.cache[date_key] = exchange_rate
                print(f"{url} downloaded, exchange rate: {exchange_rate}")
                return exchange_rate
        except (HTTPError, URLError) as ex:
            print(f"Error fetching HMRC rate: {ex}")
            raise

    def _get_daily_rate(self, date: datetime) -> float:
        """
        Get daily exchange rate from exchangerate.host.
        
        Args:
            date: The date for which to get the exchange rate
            
        Returns:
            The exchange rate from USD to GBP
        """
        date_key = date.strftime('%Y-%m-%d')
        
        if date_key in self.cache:
            print(f"Using cached exchange rate for {date_key}")
            return self.cache[date_key]
        
        url = Config.EXCHANGE_HOST_API_URL.format(
            api_key=Config.EXCHANGE_RATE_API_KEY,
            date=date_key
        )
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            exchange_rate = data["result"]
            self.cache[date_key] = exchange_rate
            print(f"{url} downloaded, exchange rate: {exchange_rate}")
            return exchange_rate

    @staticmethod
    def _parse_hmrc_xml(xml_data: str) -> float:
        """
        Parse HMRC XML response to extract USD exchange rate.
        
        Args:
            xml_data: XML string from HMRC API
            
        Returns:
            Exchange rate (inverted from the XML value)
        """
        tree = ET.fromstring(xml_data)
        for row in tree.findall('exchangeRate'):
            if row.find('currencyCode').text == 'USD':
                rate_new = float(row.find('rateNew').text)
                # HMRC provides GBP to USD, we need USD to GBP
                return 1.0 / rate_new
        raise ValueError("USD exchange rate not found in HMRC data")
