import pandas as pd

from config.settings import RAW_DATA_DIR
from data_engine.cleaner import clean_ohlc_data
from data_engine.resampler import resample_to_15_minutes


def main() -> None:
    input_path = RAW_DATA_DIR / "eurusd_1min.parquet"

    print(f"Loading: {input_path}")

    source = pd.read_parquet(input_path)
    cleaned, report = clean_ohlc_data(source)

    candles_15m = resample_to_15_minutes(
        cleaned,
        require_complete=True,
    )

    output_path = (
        RAW_DATA_DIR.parent
        / "processed"
        / "eurusd_15min.parquet"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    candles_15m.to_parquet(
        output_path,
        index=False,
    )

    print("\n1-MINUTE DATA QUALITY")
    print(f"Rows received:        {report.rows_received:,}")
    print(f"Rows cleaned:         {report.rows_cleaned:,}")
    print(f"Duplicates removed:   {report.duplicate_timestamps:,}")
    print(f"Missing values:       {report.missing_values:,}")
    print(f"Invalid timestamps:   {report.invalid_timestamps:,}")
    print(f"OHLC rows repaired:   {report.repaired_ohlc_rows:,}")
    print(f"Invalid OHLC rows:    {report.invalid_ohlc_rows:,}")
    print(f"Detected time gaps:   {report.missing_minute_intervals:,}")

    print("\n1-MINUTE RANGE")
    print(f"Start: {cleaned['timestamp'].min()}")
    print(f"End:   {cleaned['timestamp'].max()}")

    print("\n15-MINUTE OUTPUT")
    print(f"Complete candles: {len(candles_15m):,}")
    print(f"Start: {candles_15m['timestamp'].min()}")
    print(f"End:   {candles_15m['timestamp'].max()}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()