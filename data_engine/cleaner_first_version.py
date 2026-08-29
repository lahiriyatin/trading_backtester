from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = {
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "symbol",
    "interval",
}


@dataclass(frozen=True)
class DataQualityReport:
    rows_received: int
    rows_cleaned: int
    duplicate_timestamps: int
    missing_values: int
    invalid_timestamps: int
    invalid_ohlc_rows: int
    missing_minute_intervals: int


def clean_ohlc_data(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, DataQualityReport]:
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    cleaned = dataframe.copy()
    rows_received = len(cleaned)

    cleaned["timestamp"] = pd.to_datetime(
        cleaned["timestamp"],
        utc=True,
        errors="coerce",
    )

    numeric_columns = ["open", "high", "low", "close"]

    cleaned[numeric_columns] = cleaned[numeric_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    invalid_timestamps = int(cleaned["timestamp"].isna().sum())
    missing_values = int(
        cleaned[
            ["timestamp", "open", "high", "low", "close"]
        ].isna().sum().sum()
    )

    duplicate_timestamps = int(
        cleaned["timestamp"].duplicated(keep="last").sum()
    )

    invalid_ohlc_mask = (
        (cleaned["high"] < cleaned["low"])
        | (cleaned["high"] < cleaned["open"])
        | (cleaned["high"] < cleaned["close"])
        | (cleaned["low"] > cleaned["open"])
        | (cleaned["low"] > cleaned["close"])
    )

    invalid_ohlc_rows = int(invalid_ohlc_mask.sum())

    cleaned = cleaned.dropna(
        subset=["timestamp", "open", "high", "low", "close"]
    )

    cleaned = cleaned.loc[~invalid_ohlc_mask]
    cleaned = cleaned.drop_duplicates(
        subset=["timestamp"],
        keep="last",
    )

    cleaned = cleaned.sort_values("timestamp")
    cleaned = cleaned.reset_index(drop=True)

    time_differences = cleaned["timestamp"].diff()
    missing_minute_intervals = int(
        (time_differences > pd.Timedelta(minutes=1)).sum()
    )

    report = DataQualityReport(
        rows_received=rows_received,
        rows_cleaned=len(cleaned),
        duplicate_timestamps=duplicate_timestamps,
        missing_values=missing_values,
        invalid_timestamps=invalid_timestamps,
        invalid_ohlc_rows=invalid_ohlc_rows,
        missing_minute_intervals=missing_minute_intervals,
    )

    return cleaned, report