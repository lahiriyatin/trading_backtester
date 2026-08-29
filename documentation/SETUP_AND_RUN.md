# Setup and Run Guide

This guide starts from a fresh Windows PowerShell session and ends with full-dataset validation.

## 1. Open the project

```powershell
cd C:\Users\lahir\Desktop\trading_backtester
```

On a new computer:

```powershell
cd C:\Users\lahir\Desktop
git clone https://github.com/lahiriyatin/trading_backtester.git
cd trading_backtester
```

## 2. Create and activate the environment

Create it only if `.venv` does not exist:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Verify:

```powershell
python --version
where.exe python
```

The first path should point to `trading_backtester\.venv\Scripts\python.exe`.

## 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Configure the API key

```powershell
Copy-Item .env.example .env
```

Put the current key in `.env`:

```env
TWELVE_DATA_API_KEY=replace_with_your_current_key
```

Verify that Git ignores it:

```powershell
git check-ignore .env
```

Expected: `.env`.

## 5. Run the smoke test

```powershell
python main.py
```

Expected messages include project startup, the America/New_York session timezone, the configured threshold, and successful foundation loading. This also creates `logs/backtester.log`.

## 6. Run automated tests

```powershell
python -m pytest -v
```

Current expected result: `15 passed`.

## 7. Download historical data

```powershell
python -m data_engine.download_history --symbol "EUR/USD" --interval "1min"
```

The downloader requests 5,000 rows per call, waits eight seconds, saves chunks immediately, resumes before the oldest saved timestamp, deduplicates, and merges into `data/raw/eurusd_1min.parquet`.

Run only one symbol download at a time and observe the provider's current limits.

## 8. Run diagnostics

```powershell
python -m data_engine.diagnose_quality
python -m data_engine.inspect_invalid_magnitude
```

Diagnostic CSV outputs are written under `results/`.

## 9. Clean and resample the full dataset

```powershell
python -m data_engine.validate_full_dataset
```

Input:

```text
data/raw/eurusd_1min.parquet
```

Output:

```text
data/processed/eurusd_15min.parquet
```

## 10. Finish the session

```powershell
python -m pytest -v
git status
git --no-pager diff
```

Commit source and documentation only:

```powershell
git add .
git commit -m "Update project documentation"
git push
deactivate
```

## Important sample-file warning

`test_api_download.py` currently writes `data/raw/eurusd_1min.parquet`. Do not run it after downloading the full file unless you first change it to a separate sample filename, because it could overwrite the full dataset.
