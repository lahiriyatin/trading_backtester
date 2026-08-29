# Data Pipeline

## API ingestion

The loader accepts a symbol, interval, output size from 1 through 5,000, and an optional end date. Requests use UTC, ascending order, and JSON. The API key comes from the local environment file.

Request failures are reduced to safe messages so authenticated URLs are not printed.

## Historical pagination

The history downloader moves backward from the latest candle. After each request, the next end date becomes one minute before the oldest returned timestamp.

Every chunk is saved immediately with its timestamp range in the filename. On restart, the downloader finds the oldest local timestamp and continues backward. The final merge sorts and deduplicates by timestamp.

## Standard schema

| Column | Meaning |
| --- | --- |
| timestamp | UTC-aware candle-open timestamp |
| open | First recorded price |
| high | Maximum recorded price |
| low | Minimum recorded price |
| close | Final recorded price |
| symbol | Normalized symbol such as EURUSD |
| interval | Source interval such as 1min |

Volume is retained when supplied but is not required.

## Cleaning policy

The cleaner verifies columns, parses UTC timestamps, converts OHLC values, counts missing data and duplicates, measures boundary violations, repairs EUR/USD inconsistencies no larger than 0.2 pip, rejects larger corruption, sorts chronologically, and reports gaps.

Tiny repairs use:

```text
high = max(open, high, close)
low  = min(open, low, close)
```

The 0.00002 tolerance is EUR/USD-specific and must not be assumed valid for every instrument.

## Resampling

```text
open  = first one-minute open
high  = maximum one-minute high
low   = minimum one-minute low
close = last one-minute close
```

The default requires exactly 15 source candles. Partial groups and periods with missing minutes are excluded.

## Verified files

```text
data/raw/chunks/eurusd_1min/
data/raw/eurusd_1min.parquet
data/processed/eurusd_15min.parquet
```

These locations are ignored by Git.
