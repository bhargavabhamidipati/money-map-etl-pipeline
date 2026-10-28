"""Configure console logging at application startup."""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Set the console level and format, replacing previous handlers."""
    normalized_level = level.strip().upper()
    if normalized_level not in logging.getLevelNamesMapping():
        raise ValueError(f"Invalid LOG_LEVEL: {level}")

    logging.basicConfig(
        level=normalized_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
