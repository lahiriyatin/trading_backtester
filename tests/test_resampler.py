import pandas as pd

from data_engine.resampler import resample_to_15_minutes


def make_minute_data(
    start: str = "2026-08-29 10:00:00",
    periods: int = 30,
) -> pd.DataFrame:
    timestamps = pd.date_range(
        start=start,
        periods=periods,
        freq="1min",
        tz="UTC",
    )

    rows = []

    for index, timestamp in enumerate(timestamps):
        open_price = 1.1000 + index * 0.0001
        close_price = open_price + 0.00005

        rows.append(
            {
                "timestamp": timestamp,
                "open": open_price,
                "high": open_price + 0.0002,
                "low": open_price - 0.0002,
                "close": close_price,
                "symbol": "EURUSD",
                "interval": "1min",
            }
        )

    return pd.DataFrame(rows)


def test_thirty_minutes_produce_two_candles() -> None:
    source = make_minute_data(periods=30)

    result = resample_to_15_minutes(source)

    assert len(result) == 2
    assert result["source_candle_count"].tolist() == [15, 15]


def test_resampled_ohlc_is_correct() -> None:
    source = make_minute_data(periods=15)

    result = resample_to_15_minutes(source)
    candle = result.iloc[0]

    assert candle["open"] == source.iloc[0]["open"]
    assert candle["high"] == source["high"].max()
    assert candle["low"] == source["low"].min()
    assert candle["close"] == source.iloc[-1]["close"]


def test_timestamp_uses_period_open() -> None:
    source = make_minute_data(
        start="2026-08-29 10:00:00",
        periods=15,
    )

    result = resample_to_15_minutes(source)

    assert result.iloc[0]["timestamp"] == pd.Timestamp(
        "2026-08-29 10:00:00",
        tz="UTC",
    )


def test_incomplete_candle_is_excluded() -> None:
    source = make_minute_data(
        start="2026-08-29 10:09:00",
        periods=6,
    )

    result = resample_to_15_minutes(source)

    assert result.empty


def test_incomplete_candle_can_be_returned_for_diagnostics() -> None:
    source = make_minute_data(
        start="2026-08-29 10:09:00",
        periods=6,
    )

    result = resample_to_15_minutes(
        source,
        require_complete=False,
    )

    assert len(result) == 1
    assert result.iloc[0]["source_candle_count"] == 6


def test_multiple_symbols_are_rejected() -> None:
    source = make_minute_data(periods=15)
    source.loc[0, "symbol"] = "GBPUSD"

    try:
        resample_to_15_minutes(source)
    except ValueError as error:
        assert "multiple symbols" in str(error)
    else:
        raise AssertionError("Expected ValueError was not raised")