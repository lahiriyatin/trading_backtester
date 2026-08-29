import argparse
import time
from pathlib import Path

import pandas as pd

from config.settings import RAW_DATA_DIR
from data_engine.loader import TwelveDataError, fetch_time_series


ROWS_PER_REQUEST = 5000
SECONDS_BETWEEN_REQUESTS = 8
MAX_REQUESTS_PER_RUN = 790


def safe_symbol_name(symbol: str) -> str:
    return symbol.replace("/", "").lower()


def get_chunk_directory(symbol: str, interval: str) -> Path:
    directory = (
        RAW_DATA_DIR
        / "chunks"
        / f"{safe_symbol_name(symbol)}_{interval}"
    )

    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_existing_oldest_timestamp(
    chunk_directory: Path,
) -> pd.Timestamp | None:
    chunk_files = sorted(chunk_directory.glob("*.parquet"))

    if not chunk_files:
        return None

    oldest_timestamps = []

    for chunk_file in chunk_files:
        timestamps = pd.read_parquet(
            chunk_file,
            columns=["timestamp"],
        )

        oldest_timestamps.append(timestamps["timestamp"].min())

    return min(oldest_timestamps)


def save_chunk(
    dataframe: pd.DataFrame,
    chunk_directory: Path,
) -> Path:
    oldest = dataframe["timestamp"].min()
    newest = dataframe["timestamp"].max()

    filename = (
        f"{oldest.strftime('%Y%m%dT%H%M%S')}_"
        f"{newest.strftime('%Y%m%dT%H%M%S')}.parquet"
    )

    output_path = chunk_directory / filename
    dataframe.to_parquet(output_path, index=False)

    return output_path


def merge_chunks(
    symbol: str,
    interval: str,
    chunk_directory: Path,
) -> Path:
    chunk_files = sorted(chunk_directory.glob("*.parquet"))

    if not chunk_files:
        raise RuntimeError("No downloaded chunks are available to merge")

    frames = [
        pd.read_parquet(chunk_file)
        for chunk_file in chunk_files
    ]

    combined = pd.concat(frames, ignore_index=True)

    combined = combined.drop_duplicates(
        subset=["timestamp"],
        keep="last",
    )

    combined = combined.sort_values("timestamp")
    combined = combined.reset_index(drop=True)

    output_path = (
        RAW_DATA_DIR
        / f"{safe_symbol_name(symbol)}_{interval}.parquet"
    )

    combined.to_parquet(output_path, index=False)

    return output_path


def download_all_available_history(
    symbol: str,
    interval: str,
) -> None:
    chunk_directory = get_chunk_directory(symbol, interval)
    existing_oldest = get_existing_oldest_timestamp(chunk_directory)

    if existing_oldest is None:
        end_date = None
        print("No existing chunks found; starting from latest data.")
    else:
        end_date = existing_oldest - pd.Timedelta(minutes=1)
        print(f"Resuming before: {existing_oldest}")

    completed_requests = 0
    previous_oldest = existing_oldest

    try:
        while completed_requests < MAX_REQUESTS_PER_RUN:
            request_number = completed_requests + 1

            print(
                f"\nRequest {request_number}: "
                f"end_date={end_date or 'latest'}"
            )

            try:
                dataframe, _ = fetch_time_series(
                    symbol=symbol,
                    interval=interval,
                    outputsize=ROWS_PER_REQUEST,
                    end_date=end_date,
                )
            except TwelveDataError as error:
                print(f"Download stopped: {error}")
                break

            if dataframe.empty:
                print("No additional records returned.")
                break

            oldest = dataframe["timestamp"].min()
            newest = dataframe["timestamp"].max()

            if previous_oldest is not None and oldest >= previous_oldest:
                print(
                    "No older timestamps were returned; "
                    "the earliest accessible history was reached."
                )
                break

            chunk_path = save_chunk(
                dataframe,
                chunk_directory,
            )

            completed_requests += 1

            print(f"Rows received: {len(dataframe):,}")
            print(f"Range: {oldest} -> {newest}")
            print(f"Saved: {chunk_path.name}")

            previous_oldest = oldest
            end_date = oldest - pd.Timedelta(minutes=1)

            if len(dataframe) < ROWS_PER_REQUEST:
                print(
                    "A partial chunk was returned; "
                    "the earliest available history was likely reached."
                )
                break

            print(
                f"Waiting {SECONDS_BETWEEN_REQUESTS} seconds "
                "to respect the API quota..."
            )
            time.sleep(SECONDS_BETWEEN_REQUESTS)

    except KeyboardInterrupt:
        print("\nDownload interrupted. Saved chunks are preserved.")

    print("\nMerging all saved chunks...")

    output_path = merge_chunks(
        symbol,
        interval,
        chunk_directory,
    )

    combined = pd.read_parquet(
        output_path,
        columns=["timestamp"],
    )

    print("\nDOWNLOAD SUMMARY")
    print(f"Requests this run: {completed_requests}")
    print(f"Total unique rows: {len(combined):,}")
    print(f"Earliest timestamp: {combined['timestamp'].min()}")
    print(f"Latest timestamp: {combined['timestamp'].max()}")
    print(f"Final file: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download maximum accessible Twelve Data history."
    )

    parser.add_argument(
        "--symbol",
        default="EUR/USD",
        help='Twelve Data symbol, for example "EUR/USD"',
    )

    parser.add_argument(
        "--interval",
        default="1min",
        help='Candle interval, for example "1min"',
    )

    arguments = parser.parse_args()

    download_all_available_history(
        symbol=arguments.symbol,
        interval=arguments.interval,
    )


if __name__ == "__main__":
    main()