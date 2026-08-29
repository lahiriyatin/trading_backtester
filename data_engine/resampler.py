import pandas as pd


REQUIRED_COLUMNS = {
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "symbol",
}


def resample_to_15_minutes(
    dataframe: pd.DataFrame,
    require_complete: bool = True,
) -> pd.DataFrame:
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if dataframe.empty:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "symbol",
                "interval",
                "source_candle_count",
            ]
        )

    source = dataframe.copy()

    source["timestamp"] = pd.to_datetime(
        source["timestamp"],
        utc=True,
        errors="coerce",
    )

    if source["timestamp"].isna().any():
        raise ValueError("Source data contains invalid timestamps")

    if source["symbol"].nunique() != 1:
        raise ValueError(
            "Resample one symbol at a time; multiple symbols were provided"
        )

    source = source.sort_values("timestamp")
    source = source.drop_duplicates(
        subset=["timestamp"],
        keep="last",
    )

    symbol = source["symbol"].iloc[0]

    source = source.set_index("timestamp")

    resampled = source.resample(
        "15min",
        label="left",
        closed="left",
        origin="start_day",
    ).agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        source_candle_count=("close", "count"),
    )

    resampled = resampled.dropna(
        subset=["open", "high", "low", "close"]
    )

    if require_complete:
        resampled = resampled.loc[
            resampled["source_candle_count"] == 15
        ]

    resampled["symbol"] = symbol
    resampled["interval"] = "15min"

    resampled = resampled.reset_index()

    return resampled[
        [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "symbol",
            "interval",
            "source_candle_count",
        ]
    ]