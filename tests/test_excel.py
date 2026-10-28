from dataclasses import replace
from pathlib import Path

import pytest
from openpyxl import Workbook

from money_map_etl_pipeline.config.settings import Settings
from money_map_etl_pipeline.extract.excel import load_excel_file


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings('local', 'INFO', 'local', tmp_path, tmp_path / 'output',
                    None, None, 'transactions', 'sample.xlsx')


def test_load_all_sheets_without_interpreting_headers(settings: Settings) -> None:
    path = settings.local_input_dir
    workbook = Workbook()
    workbook.active.append(['Metadata', 'NA'])
    workbook.create_sheet('Transactions').append(['Amount', '12.30'])
    workbook.save(path / 'sample.xlsx')
    workbook.close()
    (path / 'other.xlsx').write_text('This unrelated workbook must not be read')
    tables = load_excel_file(settings)
    assert set(tables) == {'Sheet', 'Transactions'}
    assert tables['Sheet'].iloc[0].tolist() == ['Metadata', 'NA']
    assert tables['Transactions'].iloc[0].tolist() == ['Amount', '12.30']


@pytest.mark.parametrize('environment', ['dev', 'prod'])
def test_cloud_loading_is_explicitly_unimplemented(settings: Settings, environment: str) -> None:
    with pytest.raises(NotImplementedError, match='GCS'):
        load_excel_file(replace(settings, app_env=environment, input_source='gcs'))


def test_missing_folder(settings: Settings) -> None:
    with pytest.raises(NotADirectoryError):
        load_excel_file(replace(settings, local_input_dir=settings.local_input_dir / 'missing'))


def test_missing_configured_file(settings: Settings) -> None:
    with pytest.raises(FileNotFoundError):
        load_excel_file(settings)


def test_conflicting_source(settings: Settings) -> None:
    with pytest.raises(ValueError, match='INPUT_SOURCE'):
        load_excel_file(replace(settings, input_source='gcs'))


def test_corrupt_workbook_fails(settings: Settings) -> None:
    from zipfile import BadZipFile

    (settings.local_input_dir / 'sample.xlsx').write_text('invalid workbook')
    with pytest.raises(BadZipFile):
        load_excel_file(settings)


@pytest.mark.parametrize('filename', ['', '../sample.xlsx', '/sample.xlsx', 'sample.csv'])
def test_invalid_filename(settings: Settings, filename: str) -> None:
    with pytest.raises(ValueError, match='LOCAL_INPUT_FILE'):
        load_excel_file(replace(settings, local_input_file=filename))
