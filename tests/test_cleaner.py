import pandas as pd

from data_engine.cleaner import clean_ohlc_data


def make_valid_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": [
                "2026-08-29 11:00:00",
                "2026-08-29 11:01:00",
            ],
            "open": [1.1000, 1.1005],
            "high": [1.1010, 1.1015],
            "low": [1.0990, 1.1000],
            "close": [1.1005, 1.1010],
            "symbol": ["EURUSD", "EURUSD"],
            "interval": ["1min", "1min"],
        }
    )


def test_valid_data_is_preserved() -> None:
    dataframe = make_valid_data()

    cleaned, report = clean_ohlc_data(dataframe)

    assert len(cleaned) == 2
    assert report.rows_received == 2
    assert report.rows_cleaned == 2
    assert report.duplicate_timestamps == 0
    assert report.invalid_ohlc_rows == 0


def test_timestamps_become_utc_aware() -> None:
    dataframe = make_valid_data()

    cleaned, _ = clean_ohlc_data(dataframe)

    assert str(cleaned["timestamp"].dt.tz) == "UTC"


def test_duplicate_timestamp_is_removed() -> None:
    dataframe = make_valid_data()

    duplicate = dataframe.iloc[[1]].copy()
    dataframe = pd.concat([dataframe, duplicate], ignore_index=True)

    cleaned, report = clean_ohlc_data(dataframe)

    assert len(cleaned) == 2
    assert report.duplicate_timestamps == 1


def test_invalid_high_is_removed() -> None:
    dataframe = make_valid_data()
    dataframe.loc[0, "high"] = 1.0980

    cleaned, report = clean_ohlc_data(dataframe)

    assert len(cleaned) == 1
    assert report.invalid_ohlc_rows == 1


def test_invalid_low_is_removed() -> None:
    dataframe = make_valid_data()
    dataframe.loc[0, "low"] = 1.1020

    cleaned, report = clean_ohlc_data(dataframe)

    assert len(cleaned) == 1
    assert report.invalid_ohlc_rows == 1


def test_missing_required_column_raises_error() -> None:
    dataframe = make_valid_data().drop(columns=["close"])

    try:
        clean_ohlc_data(dataframe)
    except ValueError as error:
        assert "close" in str(error)
    else:
        raise AssertionError("Expected ValueError was not raised")


def test_data_is_sorted_chronologically() -> None:
    dataframe = make_valid_data().iloc[::-1].reset_index(drop=True)

    cleaned, _ = clean_ohlc_data(dataframe)

    assert cleaned["timestamp"].is_monotonic_increasing


######### commented so i don't need to change again
# def test_small_rounding_violation_is_repaired() -> None:
#     dataframe = make_valid_data()

#     dataframe.loc[0, "high"] = (
#         dataframe.loc[0, "open"] - 0.00002
#     )

#     cleaned, report = clean_ohlc_data(dataframe)

#     repaired = cleaned.loc[
#         cleaned["timestamp"]
#         == pd.Timestamp(
#             "2026-08-29 11:00:00",
#             tz="UTC",
#         )
#     ].iloc[0]

#     assert len(cleaned) == 2
#     assert report.repaired_ohlc_rows == 1
#     assert repaired["high"] >= repaired["open"]
#     assert repaired["high"] >= repaired["close"]

def test_small_rounding_violation_is_repaired() -> None:
    dataframe = make_valid_data()

    expected_maximum = max(
        dataframe.loc[0, "open"],
        dataframe.loc[0, "close"],
    )

    dataframe.loc[0, "high"] = (
        expected_maximum - 0.00002
    )

    cleaned, report = clean_ohlc_data(dataframe)

    repaired_rows = cleaned.loc[
        cleaned["timestamp"]
        == pd.Timestamp(
            "2026-08-29 11:00:00",
            tz="UTC",
        )
    ]

    assert len(repaired_rows) == 1

    repaired = repaired_rows.iloc[0]

    assert len(cleaned) == 2
    assert report.repaired_ohlc_rows == 1
    assert report.invalid_ohlc_rows == 0
    assert repaired["high"] == expected_maximum
    assert repaired["high"] >= repaired["open"]
    assert repaired["high"] >= repaired["close"]


def test_large_ohlc_violation_is_rejected() -> None:
    dataframe = make_valid_data()

    dataframe.loc[0, "high"] = (
        dataframe.loc[0, "open"] - 0.0010
    )

    cleaned, report = clean_ohlc_data(dataframe)

    assert len(cleaned) == 1
    assert report.invalid_ohlc_rows == 1