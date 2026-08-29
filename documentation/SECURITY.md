# Security Guide

## API keys

Store the Twelve Data key only in the local .env file:

```env
TWELVE_DATA_API_KEY=your_current_key
```

Never put a real key in source code, Markdown, commits, screenshots, public terminal output, or issues.

## Verify exclusions

```powershell
git check-ignore .env
git grep "TWELVE_DATA_API_KEY"
```

The placeholder in .env.example is expected. A real key is not.

## If a key is exposed

1. Revoke it in the provider dashboard.
2. Generate a replacement.
3. Update only local .env.
4. Confirm .env is ignored.
5. Check Git history if it may have been committed.

A committed key must be treated as compromised and rotated.

## Safe request errors

The loader handles timeout, HTTP, and general request failures without printing the complete authenticated URL. Do not restore full request exception messages because they may contain query parameters.

## Data exclusions

```text
data/raw/*
data/processed/*
results/*
logs/*.log
```

## Operational boundary

Keep the project limited to historical data engineering and educational analysis. Do not connect it to brokerage credentials, live accounts, or real-money execution.
