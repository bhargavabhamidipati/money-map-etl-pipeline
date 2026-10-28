"""Load Excel worksheets into memory without transforming their contents."""

import logging
from pathlib import Path

import pandas as pd

from ..config.settings import Settings

type ExcelSheets = dict[str, pd.DataFrame]

logger = logging.getLogger(__name__)


def load_excel_file(settings: Settings) -> ExcelSheets:
    """Load the configured workbook and return its sheets keyed by name."""
    if settings.app_env != "local":
        raise NotImplementedError("Loading an Excel file from GCS is not implemented yet")
    if settings.input_source != "local":
        raise ValueError("Local Excel loading requires INPUT_SOURCE=local")
    path = get_local_excel_path(settings)
    return read_workbook(path)


def get_local_excel_path(settings: Settings) -> Path:
    """Resolve the single configured workbook without scanning the directory."""
    filename = settings.local_input_file
    if not filename or Path(filename).name != filename:
        raise ValueError("LOCAL_INPUT_FILE must be a filename without directory components")
    directory = settings.local_input_dir
    if not directory.is_dir():
        raise NotADirectoryError(f"Local input directory does not exist: {directory}")
    path = directory / filename
    if path.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise ValueError("LOCAL_INPUT_FILE must be an .xlsx or .xlsm file")
    if not path.is_file():
        raise FileNotFoundError(f"Configured Excel file does not exist: {path}")
    return path


def read_workbook(path: Path) -> ExcelSheets:
    """Read all sheets, preserving metadata rows for later extraction."""
    logger.debug("Reading Excel workbook: %s", path)
    with pd.ExcelFile(path, engine="openpyxl") as workbook:
        return pd.read_excel(
            workbook, sheet_name=None, header=None, dtype=object,
            keep_default_na=False,
        )
