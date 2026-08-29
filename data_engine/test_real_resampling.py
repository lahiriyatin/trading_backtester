import pandas as pd

from config.settings import RAW_DATA_DIR
from data_engine.cleaner import clean_ohlc_data
from data_engine.resampler import resample_to_15_minutes


def main() -> None:
    input_path = RAW_DATA_DIR / "eurusd_1min_sample.parquet"

    source = pd.read_parquet(input_path)
    cleaned, _ = clean_ohlc_data(source)

    diagnostic = resample_to_15_minutes(
        cleaned,
        require_complete=False,
    )

    complete = resample_to_15_minutes(
        cleaned,
        require_complete=True,
    )

    print("ALL RESAMPLED PERIODS")
    print(diagnostic.to_string(index=False))

    print("\nCOMPLETE 15-MINUTE CANDLES")
    print(complete.to_string(index=False))

    print(f"\nSource 1m candles: {len(cleaned)}")
    print(f"All 15m periods: {len(diagnostic)}")
    print(f"Complete 15m candles: {len(complete)}")


if __name__ == "__main__":
    main()