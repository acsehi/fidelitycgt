# Code Architecture

This document describes the architecture of the refactored Fidelity CGT Calculator.

## Module Structure

### `config.py`
Central configuration module containing all configurable settings:
- API keys and endpoints
- Default file paths
- Stock symbols
- Feature flags

### `models.py`
Data models representing the domain objects:
- `Transaction`: Represents a buy or sell transaction for CGT calculation
- `FidelityOpenLot`: Represents an open lot from Fidelity export
- `FidelityClosedLot`: Represents a closed lot from Fidelity export

### `exchange_rate_service.py`
Service for fetching and caching exchange rates:
- Fetches rates from HMRC (preferred) or exchangerate.host API
- Caches rates to minimize API calls
- Handles fallback when HMRC data is unavailable (pre-2015)

### `csv_parser.py`
CSV parsing utilities:
- Parses Fidelity open lots CSV files
- Parses Fidelity closed lots CSV files
- Validates currency and data format

### `calculator.py`
Main calculation logic:
- `CapitalGainCalculator`: Orchestrates the conversion process
- `run()`: Backward-compatible entry point

### `capgain.py`
Simple entry point script that calls the calculator with default file names.

## Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Type Safety**: Type hints throughout for better IDE support and maintainability
3. **Testability**: Dependency injection allows for easy mocking in tests
4. **Documentation**: Comprehensive docstrings for all public APIs
5. **Configuration**: Centralized configuration for easy customization

## Data Flow

```
Fidelity CSV Files
    ↓
FidelityCSVParser → [FidelityOpenLot, FidelityClosedLot]
    ↓
CapitalGainCalculator
    ↓
ExchangeRateService → Exchange Rates (USD→GBP)
    ↓
Transaction objects
    ↓
TSV Output (for cgtcalculator.com)
```

## Error Handling

- CSV parser validates currency (must be USD)
- Exchange rate service handles API failures gracefully
- Fallback from HMRC to daily rates when needed
- Detailed error messages for debugging

## Future Improvements

1. Add logging framework instead of print statements
2. Add CLI argument parsing for file paths
3. Support for multiple stock symbols
4. Database support for caching
5. Web interface for easier use
