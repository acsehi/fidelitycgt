"""Data models for stock transactions."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class Transaction:
    """Represents a stock transaction (buy or sell)."""
    
    action: Literal['B', 'S']  # 'B' for Buy, 'S' for Sell
    date: datetime
    stock_name: str
    quantity: float
    price_gbp: float  # Price per share in GBP
    broker_cost: float = 0.0
    tax: float = 0.0

    def to_dict(self) -> dict:
        """Convert transaction to dictionary format for CSV output."""
        # Format numbers to match original output (no decimals for whole numbers)
        def format_number(num: float) -> str:
            if num == int(num):
                return str(int(num))
            return str(num)
        
        return {
            'Action': self.action,
            'Date': self.date.strftime('%d/%m/%Y'),
            'Stock_Name': self.stock_name,
            'Quantity': format_number(self.quantity),
            'price': self.price_gbp,
            'brokercost': format_number(self.broker_cost),
            'tax': format_number(self.tax)
        }


@dataclass
class FidelityOpenLot:
    """Represents an open lot from Fidelity export."""
    
    date_acquired: datetime
    quantity: float
    cost_basis: float
    cost_basis_per_share: float


@dataclass
class FidelityClosedLot:
    """Represents a closed lot from Fidelity export."""
    
    date_acquired: datetime
    quantity: float
    date_sold: datetime
    proceeds: float
    cost_basis: float
    gain_loss: float
