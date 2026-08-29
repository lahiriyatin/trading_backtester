# Project Overview

## Purpose

The project builds a reliable, testable historical OHLC data pipeline in Python. It processes information chronologically, preserves timestamps in UTC, rejects unusable records, and prevents incomplete 15-minute candles from entering later analysis.

## Implemented features

1. Project configuration and logging.
2. Twelve Data authentication through `.env`.
3. One-minute OHLC retrieval.
4. Resumable historical downloads in 5,000-row chunks.
5. Per-symbol Parquet caching.
6. Timestamp and numeric normalization.
7. Duplicate removal.
8. Conservative OHLC validation.
9. Repair of EUR/USD rounding inconsistencies no larger than 0.2 pip.
10. Rejection of larger corrupt OHLC records.
11. Gap reporting and invalid-row diagnostics.
12. Complete 15-minute resampling.
13. Automated cleaner and resampler tests.

## Not implemented

- Swing or pivot analysis
- Strategy state machine
- Entry or exit rules
- Simulated order execution
- Stop or target logic
- Portfolio accounting
- Performance analytics
- Live streaming or brokerage connectivity

The repository should currently be described as a **historical market-data foundation**, not a completed backtester.

## Technology

- Python 3.14.3
- pandas and NumPy
- requests and python-dotenv
- PyArrow and Parquet
- pytest
- Git and GitHub
- Twelve Data REST API

## Repository checkpoint

Repository: `lahiriyatin/trading_backtester`

Reviewed checkpoint: commit `b37ef0c`, titled `Complete EURUSD data validation and resampling`.

## Verified result

The downloaded history contained 2,456,032 unique one-minute rows. The cleaner repaired 1,432 tiny rounding inconsistencies and rejected 1,155 larger corrupt records. The cleaned dataset contained 2,454,877 rows and produced 157,553 complete 15-minute candles.

Long gaps mainly correspond to weekends and market holidays. Short gaps remain missing; the pipeline never invents replacement candles.
