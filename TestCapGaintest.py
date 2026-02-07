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
        self.assertEqual(lines[2], 'S\t04/04/2022\tMSFT\t10\t225.0\t0\t0\n')

    @staticmethod
    def _read_file_lines(filename: str) -> list:
        """Read all lines from a file."""
        with open(filename, 'r') as f:
            return f.readlines()


if __name__ == '__main__':
    unittest.main()
