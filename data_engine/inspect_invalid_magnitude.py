import pandas as pd

from config.settings import RAW_DATA_DIR


PIP_SIZE = 0.0001


def main() -> None:
    path = RAW_DATA_DIR / "eurusd_1min.parquet"
    dataframe = pd.read_parquet(path)

    violations = pd.DataFrame(
        {
            "timestamp": dataframe["timestamp"],
            "open_above_high": (
                dataframe["open"] - dataframe["high"]
            ).clip(lower=0),
            "close_above_high": (
                dataframe["close"] - dataframe["high"]
            ).clip(lower=0),
            "low_above_open": (
                dataframe["low"] - dataframe["open"]
            ).clip(lower=0),
            "low_above_close": (
                dataframe["low"] - dataframe["close"]
            ).clip(lower=0),
        }
    )

    violation_columns = [
        "open_above_high",
        "close_above_high",
        "low_above_open",
        "low_above_close",
    ]

    violations["maximum_violation"] = violations[
        violation_columns
    ].max(axis=1)

    violations = violations.loc[
        violations["maximum_violation"] > 0
    ].copy()

    violations["violation_pips"] = (
        violations["maximum_violation"] / PIP_SIZE
    )

    print("VIOLATION SIZE IN PIPS")
    print(
        violations["violation_pips"]
        .describe(
            percentiles=[0.50, 0.90, 0.95, 0.99]
        )
        .to_string()
    )

    print("\nLARGEST VIOLATIONS")
    print(
        violations.nlargest(
            20,
            "violation_pips",
        )[
            [
                "timestamp",
                "violation_pips",
                "open_above_high",
                "close_above_high",
                "low_above_open",
                "low_above_close",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()