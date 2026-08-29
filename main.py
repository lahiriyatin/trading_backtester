import logging

from config.settings import LOG_DIR, OTE_RETRACEMENT, SESSION_TIMEZONE


def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "backtester.log"),
            logging.StreamHandler(),
        ],
    )


def main() -> None:
    configure_logging()
    logger = logging.getLogger("backtester")

    logger.info("Trading backtester is starting")
    logger.info("Session timezone: %s", SESSION_TIMEZONE)
    logger.info("OTE threshold: %.0f%%", OTE_RETRACEMENT * 100)
    logger.info("Project foundation loaded successfully")


if __name__ == "__main__":
    main()