"""CSV parser for Fidelity transaction files."""

import csv
from datetime import datetime
from typing import List, Tuple

from models import FidelityOpenLot, FidelityClosedLot


class FidelityCSVParser:
    """Parser for Fidelity CSV export files."""

    # Expected currency in the CSV files
    EXPECTED_CURRENCY = "USD"

    @staticmethod
    def _validate_currency(row: List[str]) -> None:
        """
        Validate that the CSV file is in USD.
        
        Args:
            row: A row from the CSV file
            
        Raises:
            ValueError: If the file is in GBP instead of USD
        """
        if len(row) > 0 and row[0] == "The values are displayed in GBP":
            raise ValueError("Please download history in USD, not GBP")

    @staticmethod
    def parse_open_lots(file_path: str) -> List[FidelityOpenLot]:
        """
        Parse open lots CSV file from Fidelity.
        
        Args:
            file_path: Path to the 'View open lots.csv' file
            
        Returns:
            List of FidelityOpenLot objects
            
        Raises:
            ValueError: If file is in wrong currency
        """
        open_lots = []
        
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                FidelityCSVParser._validate_currency(row)
                
                # Skip header and empty rows
                if len(row) > 2 and row[1] != "Quantity":
                    try:
                        date_acquired = datetime.strptime(row[0], '%b-%d-%Y')
                        quantity = float(row[1])
                        cost_basis = float(row[2])
                        cost_basis_per_share = float(row[3])
                        
                        open_lots.append(FidelityOpenLot(
                            date_acquired=date_acquired,
                            quantity=quantity,
                            cost_basis=cost_basis,
                            cost_basis_per_share=cost_basis_per_share
                        ))
                    except (ValueError, IndexError) as e:
                        # Skip rows that don't match expected format
                        continue
        
        return open_lots

    @staticmethod
    def parse_closed_lots(file_path: str) -> List[FidelityClosedLot]:
        """
        Parse closed lots CSV file from Fidelity.
        
        Args:
            file_path: Path to the 'View closed lots.csv' file
            
        Returns:
            List of FidelityClosedLot objects
            
        Raises:
            ValueError: If file is in wrong currency
        """
        closed_lots = []
        
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                FidelityCSVParser._validate_currency(row)
                
                # Skip header and empty rows
                if len(row) > 2 and row[1] != "Quantity":
                    try:
                        date_acquired = datetime.strptime(row[0], '%b/%d/%Y')
                        quantity = float(row[1])
                        date_sold = datetime.strptime(row[2], '%b/%d/%Y')
                        proceeds = float(row[3])
                        cost_basis = float(row[4])
                        gain_loss = float(row[5])
                        
                        closed_lots.append(FidelityClosedLot(
                            date_acquired=date_acquired,
                            quantity=quantity,
                            date_sold=date_sold,
                            proceeds=proceeds,
                            cost_basis=cost_basis,
                            gain_loss=gain_loss
                        ))
                    except (ValueError, IndexError) as e:
                        # Skip rows that don't match expected format
                        continue
        
        return closed_lots
