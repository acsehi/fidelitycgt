"""
Capital Gains Tax Calculator for Fidelity MSFT Stock Transactions.

This module converts Fidelity transaction exports to a format readable by
http://cgtcalculator.com/, converting trades back to GBP using historical
exchange rates.
"""

import csv
from typing import List

from config import Config
from models import Transaction
from exchange_rate_service import ExchangeRateService
from csv_parser import FidelityCSVParser


class CapitalGainCalculator:
    """Calculator for capital gains tax from Fidelity stock transactions."""

    def __init__(self, exchange_rate_cache_file: str, use_hmrc_rates: bool = True):
        """
        Initialize the calculator.
        
        Args:
            exchange_rate_cache_file: Path to cache file for exchange rates
            use_hmrc_rates: Whether to use HMRC rates (True) or daily rates (False)
        """
        self.exchange_service = ExchangeRateService(
            cache_file=exchange_rate_cache_file,
            use_hmrc=use_hmrc_rates
        )

    def process_files(
        self,
        open_lots_file: str,
        closed_lots_file: str,
        output_file: str
    ) -> None:
        """
        Process Fidelity CSV files and generate CGT calculator output.
        
        Args:
            open_lots_file: Path to 'View open lots.csv' file
            closed_lots_file: Path to 'View closed lots.csv' file
            output_file: Path to output TSV file for cgtcalculator.com
        """
        # Parse input files
        open_lots = FidelityCSVParser.parse_open_lots(open_lots_file)
        closed_lots = FidelityCSVParser.parse_closed_lots(closed_lots_file)

        # Convert to transactions
        transactions = []
        
        # Process open lots (still held positions)
        for lot in open_lots:
            exchange_rate = self.exchange_service.get_exchange_rate(lot.date_acquired)
            price_gbp = lot.cost_basis_per_share * exchange_rate
            
            transaction = Transaction(
                action='B',
                date=lot.date_acquired,
                stock_name=Config.STOCK_NAME,
                quantity=lot.quantity,
                price_gbp=price_gbp
            )
            transactions.append(transaction)

        # Process closed lots (sold positions)
        for lot in closed_lots:
            # Add buy transaction
            exchange_rate_buy = self.exchange_service.get_exchange_rate(lot.date_acquired)
            cost_per_share = lot.cost_basis / lot.quantity
            price_gbp_buy = cost_per_share * exchange_rate_buy
            
            buy_transaction = Transaction(
                action='B',
                date=lot.date_acquired,
                stock_name=Config.STOCK_NAME,
                quantity=lot.quantity,
                price_gbp=price_gbp_buy
            )
            transactions.append(buy_transaction)

            # Add sell transaction
            exchange_rate_sell = self.exchange_service.get_exchange_rate(lot.date_sold)
            proceeds_per_share = lot.proceeds / lot.quantity
            price_gbp_sell = proceeds_per_share * exchange_rate_sell
            
            sell_transaction = Transaction(
                action='S',
                date=lot.date_sold,
                stock_name=Config.STOCK_NAME,
                quantity=lot.quantity,
                price_gbp=price_gbp_sell
            )
            transactions.append(sell_transaction)

        # Write output file
        self._write_output(transactions, output_file)
        
        # Save exchange rate cache
        self.exchange_service.save_cache()

    @staticmethod
    def _write_output(transactions: List[Transaction], output_file: str) -> None:
        """
        Write transactions to TSV file for cgtcalculator.com.
        
        Args:
            transactions: List of Transaction objects
            output_file: Path to output TSV file
        """
        fieldnames = ['Action', 'Date', 'Stock_Name', 'Quantity', 'price', 'brokercost', 'tax']
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
            
            for transaction in transactions:
                writer.writerow(transaction.to_dict())


def run(
    open_lots_file: str,
    closed_lots_file: str,
    output_file: str,
    exchange_rate_cache_file: str
) -> None:
    """
    Main entry point for the capital gains calculator.
    
    This function maintains backward compatibility with the original interface.
    
    Args:
        open_lots_file: Path to 'View open lots.csv' file
        closed_lots_file: Path to 'View closed lots.csv' file
        output_file: Path to output TSV file
        exchange_rate_cache_file: Path to exchange rate cache JSON file
    """
    calculator = CapitalGainCalculator(
        exchange_rate_cache_file=exchange_rate_cache_file,
        use_hmrc_rates=True
    )
    calculator.process_files(open_lots_file, closed_lots_file, output_file)
