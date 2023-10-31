import os
import unittest
from capgainCalculator import run


class TestCapGain(unittest.TestCase):
    def test_exchangeHMRC(self):
        run('tests'+os.pathsep+'View open lots.csv', 'tests'+os.pathsep+'View closed lots.csv',
            'tests'+os.pathsep+'cgt.tsv', 'tests'+os.pathsep+'exchange_rate_cache.json')
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
