# Testing Guide

## Run everything

```powershell
python -m pytest -v
```

Current verified result: 15 passed.

## Cleaner coverage

The cleaner tests verify valid-data preservation, UTC conversion, duplicate removal, invalid-high and invalid-low rejection, missing-column errors, chronological sorting, tiny rounding repair, and large-violation rejection.

## Resampler coverage

The resampler tests verify correct period counts, OHLC aggregation, period-open timestamps, incomplete-period exclusion, diagnostic partial periods, and rejection of mixed symbols.

## Manual integration programs

```text
data_engine/test_api_download.py
data_engine/test_data_quality.py
data_engine/test_real_resampling.py
```

These are manual programs, not pytest unit tests.

The latter two expect eurusd_1min_sample.parquet, while the current sample downloader writes eurusd_1min.parquet. Align the filenames before using them. The sample script can overwrite the full historical file, so give it a dedicated sample filename first.

## Syntax checks

```powershell
python -m py_compile data_engine\loader.py
python -m py_compile data_engine\cleaner.py
python -m py_compile data_engine\resampler.py
```

Every deterministic transformation should have a normal case, invalid-input case, boundary case, and explicit expected result.
