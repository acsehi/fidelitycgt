"""Main entry point for Fidelity CGT calculator."""

from calculator import run

if __name__ == '__main__':
    run('View open lots.csv', 'View closed lots.csv', 'cgt.tsv', 'exchange_rate_cache.json')