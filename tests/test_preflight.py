"""Pre-flight integration tests: validate credentials, metadata, and API access.

These run before the visual scan to catch configuration issues early.
All tests require Azure credentials and a Power BI workspace.
"""

import os

import pytest
from dotenv import load_dotenv

load_dotenv()

from pathlib import Path  # noqa: E402

from helper_functions.file_reader import read_json_files_from_folder  # noqa: E402
from helper_functions.token_helpers import (  # noqa: E402
    TestSettings,
    create_report_embed_info,
    get_access_token,
    get_api_endpoints,
    get_report_embed_token,
)

# -------------------- ENV --------------------
CLIENT_ID = os.environ.get("SP_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SP_CLIENT_SECRET")
TENANT_ID = os.environ.get("SP_TENANT_ID")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "prod")

if not CLIENT_ID or not CLIENT_SECRET or not TENANT_ID:
    raise RuntimeError("Missing required environment variables.")

# -------------------- PATHS --------------------
BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_PATH = BASE_DIR / "metadata" / "reports"
reports = read_json_files_from_folder(REPORTS_PATH)

if not reports:
    raise RuntimeError(f"No reports found in {REPORTS_PATH}")

endpoints = get_api_endpoints(ENVIRONMENT)


# -------------------- TESTS --------------------


@pytest.mark.integration
def test_required_env_vars_exist():
    assert CLIENT_ID, "SP_CLIENT_ID is missing"
    assert CLIENT_SECRET, "SP_CLIENT_SECRET is missing"
    assert TENANT_ID, "SP_TENANT_ID is missing"


@pytest.mark.integration
def test_environment_default():
    assert ENVIRONMENT in {"prod", "dev", "test", "qa"}


@pytest.mark.integration
def test_reports_loaded():
    assert len(reports) > 0


@pytest.mark.integration
def test_report_structure():
    required_fields = {"Id", "Name", "EmbedUrl", "WorkspaceId"}
    for report in reports:
        assert required_fields.issubset(report.keys())


@pytest.mark.integration
def test_report_ids_unique():
    ids = [r["Id"] for r in reports]
    assert len(ids) == len(set(ids))


@pytest.mark.integration
def test_access_token_success():
    settings = TestSettings(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        tenant_id=TENANT_ID,
        environment=ENVIRONMENT,
    )

    token = get_access_token(settings)
    assert isinstance(token, str)
    assert len(token) > 20


@pytest.mark.integration
def test_embed_token_success():
    report = reports[0]
    embed_info = create_report_embed_info(report)

    settings = TestSettings(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        tenant_id=TENANT_ID,
        environment=ENVIRONMENT,
    )

    access_token = get_access_token(settings)
    token = get_report_embed_token(embed_info, endpoints, access_token)

    assert isinstance(token, str)
    assert len(token) > 20
