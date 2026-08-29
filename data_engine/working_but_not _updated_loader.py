import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from config.settings import (
    DEFAULT_INTERVAL,
    DEFAULT_OUTPUT_SIZE,
    RAW_DATA_DIR,
    REQUEST_TIMEOUT_SECONDS,
    TWELVE_DATA_BASE_URL,
)


class TwelveDataError(RuntimeError):
    """Raised when Twelve Data returns an invalid or unsuccessful response."""


def get_api_key() -> str:
    load_dotenv()

    api_key = os.getenv("TWELVE_DATA_API_KEY")

    if not api_key:
        raise TwelveDataError(
            "TWELVE_DATA_API_KEY was not found. Add it to the project .env file."
        )

    return api_key


def fetch_time_series(
    symbol: str,
    interval: str = DEFAULT_INTERVAL,
    outputsize: int = DEFAULT_OUTPUT_SIZE,
    end_date: pd.Timestamp | str | None = None,
) -> tuple[pd.DataFrame, dict]:
    if not 1 <= outputsize <= 5000:
        raise ValueError("outputsize must be between 1 and 5000")

    endpoint = f"{TWELVE_DATA_BASE_URL}/time_series"

    parameters = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "timezone": "UTC",
        "order": "ASC",
        "format": "JSON",
        "apikey": get_api_key(),
    }

    if end_date is not None:
        parsed_end_date = pd.Timestamp(end_date)

        if parsed_end_date.tzinfo is not None:
            parsed_end_date = parsed_end_date.tz_convert("UTC")
            parsed_end_date = parsed_end_date.tz_localize(None)

        parameters["end_date"] = parsed_end_date.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    try:
        response = requests.get(
            endpoint,
            params=parameters,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise TwelveDataError(
            f"API request failed: {error}"
        ) from error

    try:
        payload = response.json()
    except ValueError as error:
        raise TwelveDataError(
            "API response was not valid JSON"
        ) from error

    if payload.get("status") == "error":
        code = payload.get("code", "unknown")
        message = payload.get("message", "Unknown API error")

        raise TwelveDataError(
            f"Twelve Data error {code}: {message}"
        )

    values = payload.get("values")

    if not values:
        raise TwelveDataError(
            f"No candle data was returned for {symbol}. "
            "The symbol, interval, requested date, or account plan "
            "may not provide access."
        )

    dataframe = pd.DataFrame(values)

    required_columns = {
        "datetime",
        "open",
        "high",
        "low",
        "close",
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise TwelveDataError(
            f"Response is missing columns: {sorted(missing_columns)}"
        )

    dataframe = dataframe.rename(
        columns={"datetime": "timestamp"}
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
    ]

    if "volume" in dataframe.columns:
        numeric_columns.append("volume")

    dataframe[numeric_columns] = dataframe[
        numeric_columns
    ].apply(
        pd.to_numeric,
        errors="coerce",
    )

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        utc=True,
        errors="coerce",
    )

    dataframe["symbol"] = symbol.replace("/", "")
    dataframe["interval"] = interval

    dataframe = dataframe.sort_values("timestamp")
    dataframe = dataframe.reset_index(drop=True)

    metadata = payload.get("meta", {})

    return dataframe, metadata


def save_raw_data(
    dataframe: pd.DataFrame,
    symbol: str,
    interval: str,
) -> Path:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    safe_symbol = symbol.replace("/", "").lower()
    safe_interval = interval.lower()

    output_path = RAW_DATA_DIR / f"{safe_symbol}_{safe_interval}.parquet"

    dataframe.to_parquet(output_path, index=False)

    return output_path
