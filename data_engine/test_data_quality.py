import pandas as pd

from config.settings import RAW_DATA_DIR
from data_engine.cleaner import clean_ohlc_data


def main() -> None:
    input_path = RAW_DATA_DIR / "eurusd_1min_sample.parquet"

    dataframe = pd.read_parquet(input_path)
    cleaned, report = clean_ohlc_data(dataframe)

    print("DATA QUALITY REPORT")
    print(f"Rows received:           {report.rows_received}")
    print(f"Rows cleaned:            {report.rows_cleaned}")
    print(f"Duplicate timestamps:    {report.duplicate_timestamps}")
    print(f"Missing values:          {report.missing_values}")
    print(f"Invalid timestamps:      {report.invalid_timestamps}")
    print(f"Invalid OHLC rows:       {report.invalid_ohlc_rows}")
    print(f"Time gaps detected:      {report.missing_minute_intervals}")

    print("\nTimestamp range")
    print(f"Start: {cleaned['timestamp'].min()}")
    print(f"End:   {cleaned['timestamp'].max()}")


if __name__ == "__main__":
    main()