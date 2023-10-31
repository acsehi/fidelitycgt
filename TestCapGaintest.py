import os
import unittest
from capgainCalculator import run


class TestCapGain(unittest.TestCase):
    def test_exchangeHMRC(self):
        run(os.path.join(os.getcwd(), 'tests', 'open.csv'),
            os.path.join(os.getcwd(), 'tests', 'closed.csv'),
            os.path.join(os.getcwd(), 'tests', 'cgt.tsv'),
            os.path.join(os.getcwd(), 'tests', 'exchange_rate_cache.json'))

        lines = self.readFileLines('tests\cgt.tsv')

        self.assertEqual(lines[0], 'B\t31/08/2023\tMSFT\t10\t150.0\t0\t0\n')
        self.assertEqual(lines[1], 'B\t28/02/2019\tMSFT\t10.0\t200.0\t0\t0\n')
        self.assertEqual(lines[2], 'S\t04/04/2022\tMSFT\t10.0\t150.0\t0\t0\n')
        self.assertEqual(len(lines), 3)

    def readFileLines(self, filename):
        with open(filename) as f:
            return f.readlines()


if __name__ == '__main__':
    unittest.main()
