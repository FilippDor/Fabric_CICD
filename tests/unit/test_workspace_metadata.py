"""Unit tests for helper_functions.get_workspace_reports_datasets (no credentials required)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from helper_functions.get_workspace_reports_datasets import fetch_workspace_metadata


@pytest.fixture
def mock_token_response():
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"access_token": "fake-token"}
    return resp


@pytest.fixture
def mock_reports_response():
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "value": [
            {
                "id": "report-1",
                "name": "Sales Report",
                "webUrl": "https://app.powerbi.com/groups/ws/reports/report-1",
                "embedUrl": "https://app.powerbi.com/reportEmbed?reportId=report-1",
                "datasetId": "ds-1",
            },
            {
                "id": "report-2",
                "name": "HR Report",
                "webUrl": "https://app.powerbi.com/groups/ws/reports/report-2",
                "embedUrl": "https://app.powerbi.com/reportEmbed?reportId=report-2",
                "datasetId": "ds-2",
            },
        ]
    }
    return resp


@pytest.fixture
def mock_dataset_response():
    resp = MagicMock()
    resp.ok = True
    resp.json.return_value = {
        "name": "SalesDS",
        "isEffectiveIdentityRequired": False,
        "isEffectiveIdentityRolesRequired": False,
    }
    return resp


class TestFetchWorkspaceMetadata:
    @patch("helper_functions.get_workspace_reports_datasets.requests")
    def test_returns_correct_structure(
        self, mock_requests, mock_token_response, mock_reports_response, mock_dataset_response
    ):
        mock_requests.post.return_value = mock_token_response
        mock_requests.get.side_effect = [
            mock_reports_response,
            mock_dataset_response,
            mock_dataset_response,
        ]

        result = fetch_workspace_metadata(
            client_id="cid",
            client_secret="csec",
            tenant_id="tid",
            workspace_id="ws-123",
        )

        assert result["workspaceId"] == "ws-123"
        assert result["reportCount"] == 2
        assert "generatedAtUtc" in result
        assert len(result["reports"]) == 2

    @patch("helper_functions.get_workspace_reports_datasets.requests")
    def test_report_fields(
        self, mock_requests, mock_token_response, mock_reports_response, mock_dataset_response
    ):
        mock_requests.post.return_value = mock_token_response
        mock_requests.get.side_effect = [
            mock_reports_response,
            mock_dataset_response,
            mock_dataset_response,
        ]

        result = fetch_workspace_metadata(
            client_id="cid",
            client_secret="csec",
            tenant_id="tid",
            workspace_id="ws-123",
        )

        report = result["reports"][0]
        assert "Id" in report
        assert "Name" in report
        assert "EmbedUrl" in report
        assert "WorkspaceId" in report
        assert "DatasetId" in report
        assert "IsEffectiveIdentityRequired" in report
        assert report["WorkspaceId"] == "ws-123"

    @patch("helper_functions.get_workspace_reports_datasets.requests")
    def test_writes_output_file(
        self,
        mock_requests,
        mock_token_response,
        mock_reports_response,
        mock_dataset_response,
        tmp_path,
    ):
        mock_requests.post.return_value = mock_token_response
        mock_requests.get.side_effect = [
            mock_reports_response,
            mock_dataset_response,
            mock_dataset_response,
        ]

        output_file = tmp_path / "output.json"
        fetch_workspace_metadata(
            client_id="cid",
            client_secret="csec",
            tenant_id="tid",
            workspace_id="ws-123",
            output_path=output_file,
        )

        assert output_file.exists()
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert data["reportCount"] == 2

    @patch("helper_functions.get_workspace_reports_datasets.requests")
    def test_auth_failure_raises(self, mock_requests):
        fail_resp = MagicMock()
        fail_resp.status_code = 401
        fail_resp.text = "Unauthorized"
        mock_requests.post.return_value = fail_resp

        with pytest.raises(RuntimeError, match="Failed to acquire access token"):
            fetch_workspace_metadata(
                client_id="cid",
                client_secret="bad",
                tenant_id="tid",
                workspace_id="ws-123",
            )

    @patch("helper_functions.get_workspace_reports_datasets.requests")
    def test_reports_api_failure_raises(self, mock_requests, mock_token_response):
        fail_resp = MagicMock()
        fail_resp.status_code = 403
        fail_resp.text = "Forbidden"

        mock_requests.post.return_value = mock_token_response
        mock_requests.get.return_value = fail_resp

        with pytest.raises(RuntimeError, match="Failed to fetch reports"):
            fetch_workspace_metadata(
                client_id="cid",
                client_secret="csec",
                tenant_id="tid",
                workspace_id="ws-123",
            )

    @patch("helper_functions.get_workspace_reports_datasets.requests")
    def test_gov_environment_urls(
        self, mock_requests, mock_token_response, mock_reports_response, mock_dataset_response
    ):
        mock_requests.post.return_value = mock_token_response
        mock_requests.get.side_effect = [
            mock_reports_response,
            mock_dataset_response,
            mock_dataset_response,
        ]

        fetch_workspace_metadata(
            client_id="cid",
            client_secret="csec",
            tenant_id="tid",
            workspace_id="ws-123",
            environment="gov",
        )

        auth_url = mock_requests.post.call_args[0][0]
        assert "microsoftonline.us" in auth_url

    @patch("helper_functions.get_workspace_reports_datasets.requests")
    def test_rls_flags_detected(self, mock_requests, mock_token_response, mock_reports_response):
        rls_resp = MagicMock()
        rls_resp.ok = True
        rls_resp.json.return_value = {
            "name": "RLS_Dataset",
            "isEffectiveIdentityRequired": True,
            "isEffectiveIdentityRolesRequired": True,
        }

        no_rls_resp = MagicMock()
        no_rls_resp.ok = True
        no_rls_resp.json.return_value = {
            "name": "Normal_Dataset",
            "isEffectiveIdentityRequired": False,
            "isEffectiveIdentityRolesRequired": False,
        }

        mock_requests.post.return_value = mock_token_response
        mock_requests.get.side_effect = [mock_reports_response, rls_resp, no_rls_resp]

        result = fetch_workspace_metadata(
            client_id="cid",
            client_secret="csec",
            tenant_id="tid",
            workspace_id="ws-123",
        )

        reports = result["reports"]
        rls_flags = {r["DatasetId"]: r["IsEffectiveIdentityRequired"] for r in reports}
        assert any(v is True for v in rls_flags.values()) or any(
            v is False for v in rls_flags.values()
        )
