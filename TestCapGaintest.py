"""Unit tests for the Capital Gains Calculator."""

import os
import unittest
from calculator import run


class TestCapGain(unittest.TestCase):
    """Test cases for capital gains calculation."""
    
    def test_exchange_hmrc(self):
        """Test processing Fidelity CSV files with HMRC exchange rates."""
        test_dir = os.path.join(os.getcwd(), 'Tests')
        
        run(
            os.path.join(test_dir, 'open.csv'),
            os.path.join(test_dir, 'closed.csv'),
            os.path.join(test_dir, 'cgt.tsv'),
            os.path.join(test_dir, 'exchange_rate_cache.json')
        )

        lines = self._read_file_lines(os.path.join(test_dir, 'cgt.tsv'))

        # Verify the correct number of transactions
        self.assertEqual(len(lines), 3)
        
        # Verify first line (open lot buy)
        self.assertEqual(lines[0], 'B\t31/08/2023\tMSFT\t10\t150.0\t0\t0\n')
        
        # Verify second line (closed lot buy)
        self.assertEqual(lines[1], 'B\t28/02/2019\tMSFT\t10\t200.0\t0\t0\n')
        
        # Verify third line (closed lot sell)
        # Note: Value is 225.0 because proceeds (1500) / quantity (10) * exchange_rate (1.5) = 225
        self.assertEqual(lines[2], 'S\t04/04/2022\tMSFT\t10\t225.0\t0\t0\n')

    def test_fractional_quantities(self):
        """Test that fractional quantities are formatted correctly."""
        test_dir = os.path.join(os.getcwd(), 'Tests')
        
        # Create a cache file with specific rates for this test
        cache_data = {
            "2023-08": 0.5,
            "2020-03": 1.2,
            "2023-05": 0.8
        }
        cache_file = os.path.join(test_dir, 'exchange_rate_cache_fractional.json')
        with open(cache_file, 'w') as f:
            import json
            json.dump(cache_data, f)
        
        run(
            os.path.join(test_dir, 'open_fractional.csv'),
            os.path.join(test_dir, 'closed_fractional.csv'),
            os.path.join(test_dir, 'cgt_fractional.tsv'),
            cache_file
        )

        lines = self._read_file_lines(os.path.join(test_dir, 'cgt_fractional.tsv'))

        # Verify fractional quantities are shown with decimals
        self.assertIn('12.5', lines[0])  # Open lot with fractional quantity
        self.assertIn('7.5', lines[1])   # Closed lot buy with fractional quantity
        self.assertIn('7.5', lines[2])   # Closed lot sell with fractional quantity
        
        # Clean up
        os.remove(cache_file)
        os.remove(os.path.join(test_dir, 'cgt_fractional.tsv'))

    @staticmethod
    def _read_file_lines(filename: str) -> list:
        """Read all lines from a file."""
        with open(filename, 'r') as f:
            return f.readlines()


if __name__ == '__main__':
    unittest.main()
