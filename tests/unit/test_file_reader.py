"""Unit tests for helper_functions.file_reader (no credentials required)."""

import json

import pytest

from helper_functions.file_reader import read_json_files_from_folder


class TestReadJsonFilesFromFolder:
    def test_reads_single_file(self, tmp_path):
        data = {
            "reports": [
                {"Id": "r1", "Name": "Report 1"},
                {"Id": "r2", "Name": "Report 2"},
            ]
        }
        (tmp_path / "workspace.json").write_text(json.dumps(data), encoding="utf-8")

        result = read_json_files_from_folder(tmp_path)

        assert len(result) == 2
        assert result[0]["Id"] == "r1"
        assert result[1]["Id"] == "r2"

    def test_reads_multiple_files(self, tmp_path):
        file1 = {"reports": [{"Id": "r1", "Name": "Report 1"}]}
        file2 = {"reports": [{"Id": "r2", "Name": "Report 2"}]}
        (tmp_path / "ws1.json").write_text(json.dumps(file1), encoding="utf-8")
        (tmp_path / "ws2.json").write_text(json.dumps(file2), encoding="utf-8")

        result = read_json_files_from_folder(tmp_path)

        assert len(result) == 2
        ids = {r["Id"] for r in result}
        assert ids == {"r1", "r2"}

    def test_empty_reports_array(self, tmp_path):
        data = {"reports": []}
        (tmp_path / "empty.json").write_text(json.dumps(data), encoding="utf-8")

        result = read_json_files_from_folder(tmp_path)

        assert result == []

    def test_no_reports_key(self, tmp_path):
        data = {"other_key": "value"}
        (tmp_path / "no_reports.json").write_text(json.dumps(data), encoding="utf-8")

        result = read_json_files_from_folder(tmp_path)

        assert result == []

    def test_empty_folder(self, tmp_path):
        result = read_json_files_from_folder(tmp_path)

        assert result == []

    def test_missing_folder_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_json_files_from_folder(tmp_path / "nonexistent")

    def test_file_path_raises(self, tmp_path):
        f = tmp_path / "file.json"
        f.write_text("{}", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            read_json_files_from_folder(f)

    def test_malformed_json_skipped(self, tmp_path, capsys):
        (tmp_path / "bad.json").write_text("not valid json", encoding="utf-8")
        good = {"reports": [{"Id": "r1", "Name": "Good"}]}
        (tmp_path / "good.json").write_text(json.dumps(good), encoding="utf-8")

        result = read_json_files_from_folder(tmp_path)

        assert len(result) == 1
        assert result[0]["Id"] == "r1"
