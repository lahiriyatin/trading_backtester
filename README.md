# Trading Backtester Data Foundation

This repository currently implements the historical market-data foundation for a Python research project. It downloads one-minute OHLC data from Twelve Data, caches it as Parquet, validates and cleans it, resamples complete one-minute groups into 15-minute candles, and verifies deterministic behavior with pytest.

The current code does **not** implement a completed strategy engine, simulated order execution, portfolio management, or live brokerage connectivity. The `strategy/`, `execution/`, `backtest/`, and `indicators/swings.py` areas are currently placeholders.

## Current verified result

| Metric | Result |
| --- | ---: |
| Raw one-minute rows | 2,456,032 |
| Cleaned one-minute rows | 2,454,877 |
| Tiny OHLC inconsistencies repaired | 1,432 |
| Corrupted OHLC rows rejected | 1,155 |
| Detected gaps after cleaning | 11,501 |
| Complete 15-minute candles | 157,553 |
| Earliest one-minute timestamp | 2020-04-07 06:54 UTC |
| Latest one-minute timestamp | 2026-08-29 13:29 UTC |
| Automated tests | 15 passing |

## Documentation

- [Project overview](documentation/PROJECT_OVERVIEW.md)
- [Setup and run guide](documentation/SETUP_AND_RUN.md)
- [Architecture](documentation/ARCHITECTURE.md)
- [Data pipeline](documentation/DATA_PIPELINE.md)
- [Testing](documentation/TESTING.md)
- [Progress](documentation/PROGRESS.md)
- [Security](documentation/SECURITY.md)
- [Troubleshooting](documentation/TROUBLESHOOTING.md)

## Quick start

```powershell
\trading_backtester
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
python -m pytest -v
```

Validate the downloaded EUR/USD dataset:

```powershell
python -m data_engine.validate_full_dataset
```

See the setup guide for the complete workflow.

## Data and secrets

Never commit `.env`, API keys, raw or processed Parquet data, diagnostic results, or runtime logs.

The project is intended for historical data engineering and educational analysis. It is not financial advice and must not be connected to live brokerage execution.
