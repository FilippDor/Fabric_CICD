"""Unit tests for helper_functions.token_helpers (no credentials required)."""

from unittest.mock import MagicMock, patch

import pytest

from helper_functions.token_helpers import (
    ReportEmbedInfo,
    TestSettings,
    create_report_embed_info,
    get_access_token,
    get_api_endpoints,
    get_report_embed_token,
)

# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def settings():
    return TestSettings(
        client_id="test-client-id",
        client_secret="test-client-secret",
        tenant_id="test-tenant-id",
        environment="prod",
    )


@pytest.fixture
def endpoints():
    return get_api_endpoints("prod")


@pytest.fixture
def embed_info():
    return ReportEmbedInfo(
        report_id="report-123",
        workspace_id="workspace-456",
        dataset_id="dataset-789",
    )


@pytest.fixture
def sample_report():
    return {
        "Id": "report-123",
        "Name": "Sales Report",
        "EmbedUrl": "https://app.powerbi.com/reportEmbed?reportId=report-123",
        "WebUrl": "https://app.powerbi.com/groups/ws/reports/report-123",
        "DatasetId": "dataset-789",
        "WorkspaceId": "workspace-456",
        "IsEffectiveIdentityRequired": False,
        "IsEffectiveIdentityRolesRequired": False,
    }


# ── get_access_token ──────────────────────────────────────────────────


class TestGetAccessToken:
    @patch("helper_functions.token_helpers.requests.post")
    def test_returns_token_on_success(self, mock_post, settings):
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "fake-access-token-xyz"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        token = get_access_token(settings)

        assert token == "fake-access-token-xyz"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "oauth2/v2.0/token" in call_args[0][0]
        assert call_args[1]["data"]["client_id"] == "test-client-id"

    @patch("helper_functions.token_helpers.requests.post")
    def test_raises_on_http_error(self, mock_post, settings):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="401 Unauthorized"):
            get_access_token(settings)

    @patch("helper_functions.token_helpers.requests.post")
    def test_raises_on_missing_token_field(self, mock_post, settings):
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "invalid_grant"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="Failed to get access token"):
            get_access_token(settings)


# ── get_report_embed_token ────────────────────────────────────────────


class TestGetReportEmbedToken:
    @patch("helper_functions.token_helpers.requests.post")
    def test_returns_embed_token(self, mock_post, embed_info, endpoints):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"token": "embed-token-abc"}
        mock_post.return_value = mock_response

        token = get_report_embed_token(embed_info, endpoints, "fake-access-token")

        assert token == "embed-token-abc"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "GenerateToken" in call_args[0][0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer fake-access-token"

    @patch("helper_functions.token_helpers.requests.post")
    def test_no_identity_when_rls_not_required(self, mock_post, embed_info, endpoints):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"token": "embed-token-abc"}
        mock_post.return_value = mock_response

        get_report_embed_token(embed_info, endpoints, "fake-access-token")

        body = mock_post.call_args[1]["json"]
        assert "identities" not in body

    @patch("helper_functions.token_helpers.requests.post")
    def test_includes_identity_when_rls_required(self, mock_post, endpoints):
        info = ReportEmbedInfo(
            report_id="report-123",
            workspace_id="workspace-456",
            dataset_id="dataset-789",
            role="Viewer",
            is_effective_identity_required=True,
            is_effective_identity_roles_required=True,
        )
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"token": "embed-token-rls"}
        mock_post.return_value = mock_response

        token = get_report_embed_token(info, endpoints, "fake-access-token")

        assert token == "embed-token-rls"
        body = mock_post.call_args[1]["json"]
        assert "identities" in body
        identity = body["identities"][0]
        assert identity["username"] == "TestUser"
        assert identity["datasets"] == ["dataset-789"]
        assert identity["roles"] == ["Viewer"]

    @patch("helper_functions.token_helpers.requests.post")
    def test_raises_on_api_error(self, mock_post, embed_info, endpoints):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="GenerateToken failed"):
            get_report_embed_token(embed_info, endpoints, "fake-access-token")

    @patch("helper_functions.token_helpers.requests.post")
    def test_raises_on_missing_token_field(self, mock_post, embed_info, endpoints):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"error": "something went wrong"}
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="Failed to get embed token"):
            get_report_embed_token(embed_info, endpoints, "fake-access-token")


# ── create_report_embed_info ──────────────────────────────────────────


class TestCreateReportEmbedInfo:
    def test_basic_report(self, sample_report):
        info = create_report_embed_info(sample_report)

        assert info.report_id == "report-123"
        assert info.workspace_id == "workspace-456"
        assert info.dataset_id == "dataset-789"
        assert info.is_effective_identity_required is False
        assert info.is_effective_identity_roles_required is False
        assert info.role is None
        assert info.page_id is None

    def test_report_with_rls(self, sample_report):
        sample_report["IsEffectiveIdentityRequired"] = True
        sample_report["IsEffectiveIdentityRolesRequired"] = True
        sample_report["Role"] = "Admin"

        info = create_report_embed_info(sample_report)

        assert info.is_effective_identity_required is True
        assert info.is_effective_identity_roles_required is True
        assert info.role == "Admin"

    def test_report_with_pages(self, sample_report):
        sample_report["Pages"] = ["page-1", "page-2"]

        info = create_report_embed_info(sample_report)

        assert info.page_id == "page-1"

    def test_missing_workspace_id_raises(self):
        with pytest.raises(ValueError, match="missing WorkspaceId"):
            create_report_embed_info({"Id": "r1", "Name": "Test"})

    def test_missing_report_id_raises(self):
        with pytest.raises(ValueError, match="missing reportId"):
            create_report_embed_info({"Name": "Test", "WorkspaceId": "ws1"})


# ── get_api_endpoints ─────────────────────────────────────────────────


class TestGetApiEndpoints:
    def test_prod_environment(self):
        ep = get_api_endpoints("prod")
        assert ep.api_prefix == "https://api.powerbi.com"
        assert ep.web_prefix == "https://app.powerbi.com"

    def test_gov_environment(self):
        ep = get_api_endpoints("gov")
        assert ep.api_prefix == "https://api.powerbigov.us"
        assert ep.web_prefix == "https://app.powerbigov.us"

    def test_case_insensitive(self):
        ep = get_api_endpoints("PROD")
        assert ep.api_prefix == "https://api.powerbi.com"

    def test_unknown_environment_raises(self):
        with pytest.raises(ValueError, match="Unknown environment"):
            get_api_endpoints("staging")
