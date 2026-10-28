import logging

from .config.logging import configure_logging
from .config.settings import get_settings
from .extract.excel import load_excel_file

logger = logging.getLogger(__name__)


def main() -> None:
    """Configure logging and load source workbooks for processing."""
    configure_logging()
    try:
        settings = get_settings()
        configure_logging(settings.log_level)
        logger.info("Starting pipeline (environment=%s)", settings.app_env)
        sheets = load_excel_file(settings)
        logger.info("Loaded Excel file with %d sheets into memory", len(sheets))
    except Exception:
        logger.exception("Pipeline failed")
        raise SystemExit(1) from None
