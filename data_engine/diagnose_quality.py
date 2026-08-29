import pandas as pd

from config.settings import RAW_DATA_DIR, RESULTS_DIR


def main() -> None:
    input_path = RAW_DATA_DIR / "eurusd_1min.parquet"
    dataframe = pd.read_parquet(input_path)

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        utc=True,
    )

    conditions = {
        "high_below_low":
            dataframe["high"] < dataframe["low"],

        "high_below_open":
            dataframe["high"] < dataframe["open"],

        "high_below_close":
            dataframe["high"] < dataframe["close"],

        "low_above_open":
            dataframe["low"] > dataframe["open"],

        "low_above_close":
            dataframe["low"] > dataframe["close"],
    }

    invalid_mask = pd.Series(
        False,
        index=dataframe.index,
    )

    print("INVALID OHLC BREAKDOWN")

    for name, condition in conditions.items():
        count = int(condition.sum())
        invalid_mask |= condition
        print(f"{name:20}: {count:,}")

    invalid_rows = dataframe.loc[invalid_mask].copy()

    print(f"\nUnique invalid rows: {len(invalid_rows):,}")

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    invalid_output = RESULTS_DIR / "invalid_ohlc_rows.csv"
    invalid_rows.to_csv(invalid_output, index=False)

    sorted_data = dataframe.sort_values("timestamp").copy()
    sorted_data["time_difference"] = (
        sorted_data["timestamp"].diff()
    )

    gaps = sorted_data.loc[
        sorted_data["time_difference"]
        > pd.Timedelta(minutes=1)
    ].copy()

    gaps["gap_minutes"] = (
        gaps["time_difference"].dt.total_seconds() / 60
    )

    print("\nGAP BREAKDOWN")
    print(f"2-5 minutes:    {gaps['gap_minutes'].between(2, 5).sum():,}")
    print(f"6-60 minutes:   {gaps['gap_minutes'].between(6, 60).sum():,}")
    print(f"1-24 hours:     {gaps['gap_minutes'].between(61, 1440).sum():,}")
    print(f"Over 24 hours:  {(gaps['gap_minutes'] > 1440).sum():,}")

    print("\nLARGEST GAPS")
    print(
        gaps[
            ["timestamp", "time_difference", "gap_minutes"]
        ]
        .nlargest(20, "gap_minutes")
        .to_string(index=False)
    )

    gaps_output = RESULTS_DIR / "timestamp_gaps.csv"
    gaps.to_csv(gaps_output, index=False)

    print(f"\nInvalid rows saved: {invalid_output}")
    print(f"Gap report saved:   {gaps_output}")


if __name__ == "__main__":
    main()