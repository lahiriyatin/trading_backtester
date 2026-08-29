# Troubleshooting

## Environment will not activate

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

## Wrong Python interpreter

```powershell
where.exe python
```

The first path must point into the project virtual environment.

## Missing setting import

Confirm config/settings.py defines the API base URL, default interval, default output size, and request timeout.

## Request timeout

Completed chunks remain saved. Rerun:

```powershell
python -m data_engine.download_history --symbol "EUR/USD" --interval "1min"
```

If necessary, raise the request timeout from 30 to 60 seconds.

## HTTP 404 at the oldest timestamp

After a large successful download, this can indicate the earliest accessible boundary. Saved chunks are still merged.

## API key appears in output

Revoke and replace it immediately. Confirm the loader uses sanitized error handling.

## Requirements appear binary in Git

```powershell
python -m pip freeze | Out-File -FilePath requirements.txt -Encoding utf8
```

## Git opens its pager

Press q, or run:

```powershell
git --no-pager diff
```

## Duplicate tests are collected

Rename backup files so they do not begin with test_, or rely on Git history.

## Sample file mismatch

Some manual scripts expect eurusd_1min_sample.parquet, but the current sample downloader writes eurusd_1min.parquet. Align filenames first.

## Full dataset overwritten by sample

Give the sample downloader a dedicated filename before running it when the full dataset exists.

## Incomplete 15-minute candles disappear

This is intentional. The default retains only groups with exactly 15 source candles.
