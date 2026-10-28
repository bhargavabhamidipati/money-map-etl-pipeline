import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

from dotenv import load_dotenv

Environment = Literal["local", "dev", "prod"]
InputSource = Literal["local", "gcs"]


@dataclass(frozen=True)
class Settings:
    app_env: Environment
    log_level: str
    input_source: InputSource

    local_input_dir: Path
    local_output_dir: Path

    gcp_project_id: str | None
    gcs_bucket_name: str | None
    firestore_collection: str
    local_input_file: str


def get_settings(env_file: str | Path = ".env") -> Settings:
    """Load local configuration without overriding existing environment variables."""
    load_dotenv(dotenv_path=env_file, override=False)
    app_env = _get_environment()
    input_source = _get_input_source(app_env)
    settings = _build_settings(app_env, input_source)
    _validate_cloud_settings(settings)
    return settings


def _get_environment() -> Environment:
    """Read and validate the application environment."""
    app_env = os.getenv("APP_ENV", "local")
    if app_env not in ("local", "dev", "prod"):
        raise ValueError(f"Invalid APP_ENV: {app_env}")
    return cast(Environment, app_env)


def _get_input_source(app_env: Environment) -> InputSource:
    """Read the input source and check compatibility with the environment."""
    input_source = os.getenv("INPUT_SOURCE", "local")
    if input_source not in ("local", "gcs"):
        raise ValueError(f"Invalid INPUT_SOURCE: {input_source}")
    if app_env != "local" and input_source != "gcs":
        raise ValueError("Cloud environments must use GCS input")
    return cast(InputSource, input_source)


def _build_settings(app_env: Environment, input_source: InputSource) -> Settings:
    """Build settings from environment variables and their defaults."""
    return Settings(
        app_env=app_env,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        input_source=input_source,
        local_input_file=os.getenv("LOCAL_INPUT_FILE", ""),
        local_input_dir=Path(
            os.getenv("LOCAL_INPUT_DIR", "data/raw")
        ),
        local_output_dir=Path(
            os.getenv("LOCAL_OUTPUT_DIR", "data/processed")
        ),
        gcp_project_id=os.getenv("GCP_PROJECT_ID") or None,
        gcs_bucket_name=os.getenv("GCS_BUCKET_NAME") or None,
        firestore_collection=os.getenv(
            "FIRESTORE_COLLECTION", "transactions"
        ),
    )


def _validate_cloud_settings(settings: Settings) -> None:
    """Require cloud resource identifiers for non-local environments."""
    if settings.app_env == "local":
        return

    if not settings.gcp_project_id:
        raise ValueError("GCP_PROJECT_ID is required")
    if not settings.gcs_bucket_name:
        raise ValueError("GCS_BUCKET_NAME is required")
