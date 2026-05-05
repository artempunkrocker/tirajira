"""
Tests for linking functionality in all file loaders.
"""

import csv
import json
from unittest.mock import MagicMock, Mock, mock_open, patch

import yaml

from tirajira.file_loaders.csv_loader import CsvFileLoader
from tirajira.file_loaders.excel_loader import ExcelFileLoader
from tirajira.file_loaders.json_loader import JsonFileLoader
from tirajira.file_loaders.xml_loader import XmlFileLoader
from tirajira.file_loaders.yaml_loader import YamlFileLoader


class TestFileLoaderLinking:
    """Tests for linking functionality in all file loaders."""

    LINKING_TEST_DATA = [
        {
            "project": {"key": "PROJ"},
            "summary": "Task with single link",
            "issuetype": {"name": "Task"},
            "linking": {"target_key": "PROJ-123", "link_type": "relates to"},
        },
        {
            "project": {"key": "PROJ"},
            "summary": "Task with multiple links",
            "issuetype": {"name": "Bug"},
            "linking": [
                {"target_key": "PROJ-123", "link_type": "relates to"},
                {"target_key": "PROJ-456", "link_type": "blocks"},
            ],
        },
    ]

    def test_json_loader_with_linking(self):
        single_link_data = [self.LINKING_TEST_DATA[0]]
        json_content = json.dumps(single_link_data, ensure_ascii=False, indent=2)

        with patch("builtins.open", mock_open(read_data=json_content)):
            with patch("os.path.exists", return_value=True):
                loader = JsonFileLoader()
                issues = loader.load_issues("test.json")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], dict)
                assert issue["linking"]["target_key"] == "PROJ-123"
                assert issue["linking"]["link_type"] == "relates to"

        multiple_links_data = [self.LINKING_TEST_DATA[1]]
        json_content = json.dumps(multiple_links_data, ensure_ascii=False, indent=2)

        with patch("builtins.open", mock_open(read_data=json_content)):
            with patch("os.path.exists", return_value=True):
                loader = JsonFileLoader()
                issues = loader.load_issues("test.json")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], list)
                assert len(issue["linking"]) == 2
                assert issue["linking"][0]["target_key"] == "PROJ-123"
                assert issue["linking"][0]["link_type"] == "relates to"
                assert issue["linking"][1]["target_key"] == "PROJ-456"
                assert issue["linking"][1]["link_type"] == "blocks"

    def test_yaml_loader_with_linking(self):
        single_link_data = [self.LINKING_TEST_DATA[0]]
        yaml_content = yaml.dump(single_link_data, allow_unicode=True)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("os.path.exists", return_value=True):
                loader = YamlFileLoader()
                issues = loader.load_issues("test.yaml")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], dict)
                assert issue["linking"]["target_key"] == "PROJ-123"
                assert issue["linking"]["link_type"] == "relates to"

        multiple_links_data = [self.LINKING_TEST_DATA[1]]
        yaml_content = yaml.dump(multiple_links_data, allow_unicode=True)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("os.path.exists", return_value=True):
                loader = YamlFileLoader()
                issues = loader.load_issues("test.yaml")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], list)
                assert len(issue["linking"]) == 2
                assert issue["linking"][0]["target_key"] == "PROJ-123"
                assert issue["linking"][0]["link_type"] == "relates to"
                assert issue["linking"][1]["target_key"] == "PROJ-456"
                assert issue["linking"][1]["link_type"] == "blocks"

    def test_csv_loader_with_linking(self):
        mock_reader = MagicMock()
        mock_reader.fieldnames = [
            "project.key",
            "summary",
            "issuetype.name",
            "linking.target_key",
            "linking.link_type",
        ]
        mock_reader.__iter__ = Mock(
            return_value=iter(
                [
                    {
                        "project.key": "PROJ",
                        "summary": "Task with single link",
                        "issuetype.name": "Task",
                        "linking.target_key": "PROJ-123",
                        "linking.link_type": "relates to",
                    }
                ]
            )
        )

        with patch("builtins.open", mock_open(read_data="")):
            with patch("os.path.exists", return_value=True):
                with patch("csv.DictReader", return_value=mock_reader):
                    with patch("csv.Sniffer.sniff") as mock_sniffer:
                        mock_dialect = csv.excel()
                        mock_dialect.delimiter = ","
                        mock_sniffer.return_value = mock_dialect

                        loader = CsvFileLoader()
                        issues = loader.load_issues("test.csv")

                        assert len(issues) == 1
                        issue = issues[0]
                        assert "linking" in issue
                        assert isinstance(issue["linking"], dict)
                        assert issue["linking"]["target_key"] == "PROJ-123"
                        assert issue["linking"]["link_type"] == "relates to"

        mock_reader = MagicMock()
        mock_reader.fieldnames = [
            "project.key",
            "summary",
            "issuetype.name",
            "linking.0.target_key",
            "linking.0.link_type",
            "linking.1.target_key",
            "linking.1.link_type",
        ]
        mock_reader.__iter__ = Mock(
            return_value=iter(
                [
                    {
                        "project.key": "PROJ",
                        "summary": "Task with multiple links",
                        "issuetype.name": "Bug",
                        "linking.0.target_key": "PROJ-123",
                        "linking.0.link_type": "relates to",
                        "linking.1.target_key": "PROJ-456",
                        "linking.1.link_type": "blocks",
                    }
                ]
            )
        )

        with patch("builtins.open", mock_open(read_data="")):
            with patch("os.path.exists", return_value=True):
                with patch("csv.DictReader", return_value=mock_reader):
                    with patch("csv.Sniffer.sniff") as mock_sniffer:
                        mock_dialect = csv.excel()
                        mock_dialect.delimiter = ","
                        mock_sniffer.return_value = mock_dialect

                        loader = CsvFileLoader()
                        issues = loader.load_issues("test.csv")

                        assert len(issues) == 1
                        issue = issues[0]
                        assert "linking" in issue
                        assert isinstance(issue["linking"], list)
                        assert len(issue["linking"]) == 2
                        assert issue["linking"][0]["target_key"] == "PROJ-123"
                        assert issue["linking"][0]["link_type"] == "relates to"
                        assert issue["linking"][1]["target_key"] == "PROJ-456"
                        assert issue["linking"][1]["link_type"] == "blocks"

    def _create_mock_excel_with_linking(self, test_data):
        from unittest.mock import MagicMock

        mock_sheet = MagicMock()
        mock_sheet.max_row = len(test_data) + 1
        mock_sheet.max_column = 10

        headers = {}
        col_index = 1

        headers[(1, col_index)] = "project.key"
        col_index += 1
        headers[(1, col_index)] = "summary"
        col_index += 1
        headers[(1, col_index)] = "issuetype.name"
        col_index += 1

        linking_data = test_data[0].get("linking")
        if isinstance(linking_data, dict):
            headers[(1, col_index)] = "linking.target_key"
            col_index += 1
            headers[(1, col_index)] = "linking.link_type"
        elif isinstance(linking_data, list):
            for i in range(len(linking_data)):
                headers[(1, col_index)] = f"linking.{i}.target_key"
                col_index += 1
                headers[(1, col_index)] = f"linking.{i}.link_type"
                col_index += 1

        cell_values = {}
        cell_values.update(headers)

        for i, issue in enumerate(test_data):
            row_idx = i + 2
            col_idx = 1

            cell_values[(row_idx, col_idx)] = issue["project"]["key"]
            col_idx += 1
            cell_values[(row_idx, col_idx)] = issue["summary"]
            col_idx += 1
            cell_values[(row_idx, col_idx)] = issue["issuetype"]["name"]
            col_idx += 1

            linking_data = issue.get("linking")
            if isinstance(linking_data, dict):
                cell_values[(row_idx, col_idx)] = linking_data["target_key"]
                col_idx += 1
                cell_values[(row_idx, col_idx)] = linking_data["link_type"]
            elif isinstance(linking_data, list):
                for link_item in linking_data:
                    cell_values[(row_idx, col_idx)] = link_item["target_key"]
                    col_idx += 1
                    cell_values[(row_idx, col_idx)] = link_item["link_type"]
                    col_idx += 1

        mock_sheet.cell.side_effect = lambda row, column: MagicMock(
            value=cell_values.get((row, column), None)
        )

        mock_workbook = MagicMock()
        mock_workbook.active = mock_sheet
        mock_workbook.close = MagicMock()

        return mock_workbook

    def test_excel_loader_with_linking(self):
        single_link_data = [self.LINKING_TEST_DATA[0]]
        mock_workbook = self._create_mock_excel_with_linking(single_link_data)

        with patch("os.path.exists", return_value=True):
            with patch(
                "tirajira.file_loaders.excel_loader.load_workbook",
                return_value=mock_workbook,
            ):
                with patch.object(ExcelFileLoader, "_validate_and_open_file"):
                    loader = ExcelFileLoader()
                    issues = loader.load_issues("test.xlsx")

                    assert len(issues) == 1
                    issue = issues[0]
                    assert "linking" in issue
                    assert isinstance(issue["linking"], dict)
                    assert issue["linking"]["target_key"] == "PROJ-123"
                    assert issue["linking"]["link_type"] == "relates to"

        multiple_links_data = [self.LINKING_TEST_DATA[1]]
        mock_workbook = self._create_mock_excel_with_linking(multiple_links_data)

        with patch("os.path.exists", return_value=True):
            with patch(
                "tirajira.file_loaders.excel_loader.load_workbook",
                return_value=mock_workbook,
            ):
                with patch.object(ExcelFileLoader, "_validate_and_open_file"):
                    loader = ExcelFileLoader()
                    issues = loader.load_issues("test.xlsx")

                    assert len(issues) == 1
                    issue = issues[0]
                    assert "linking" in issue
                    assert isinstance(issue["linking"], list)
                    assert len(issue["linking"]) == 2
                    assert issue["linking"][0]["target_key"] == "PROJ-123"
                    assert issue["linking"][0]["link_type"] == "relates to"
                    assert issue["linking"][1]["target_key"] == "PROJ-456"
                    assert issue["linking"][1]["link_type"] == "blocks"

    @staticmethod
    def _convert_to_xml_with_linking(data):
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?><issues>']

        for issue in data:
            xml_parts.append("<issue>")

            for key, value in issue.items():
                if key == "linking":
                    xml_parts.append("<linking>")
                    if isinstance(value, dict):
                        xml_parts.append(
                            f"<target_key>{value['target_key']}</target_key>"
                        )
                        xml_parts.append(f"<link_type>{value['link_type']}</link_type>")
                    elif isinstance(value, list):
                        for link_item in value:
                            xml_parts.append("<link>")
                            xml_parts.append(
                                f"<target_key>{link_item['target_key']}</target_key>"
                            )
                            xml_parts.append(
                                f"<link_type>{link_item['link_type']}</link_type>"
                            )
                            xml_parts.append("</link>")
                    xml_parts.append("</linking>")
                elif isinstance(value, dict):
                    xml_parts.append(f"<{key}>")
                    for sub_key, sub_value in value.items():
                        xml_parts.append(f"<{sub_key}>{sub_value}</{sub_key}>")
                    xml_parts.append(f"</{key}>")
                else:
                    xml_parts.append(f"<{key}>{value}</{key}>")

            xml_parts.append("</issue>")

        xml_parts.append("</issues>")
        return "".join(xml_parts)

    def test_xml_loader_with_linking(self):
        single_link_data = [self.LINKING_TEST_DATA[0]]
        xml_content = self._convert_to_xml_with_linking(single_link_data)

        with patch("builtins.open", mock_open(read_data=xml_content)):
            with patch("os.path.exists", return_value=True):
                loader = XmlFileLoader()
                issues = loader.load_issues("test.xml")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], dict)
                assert issue["linking"]["target_key"] == "PROJ-123"
                assert issue["linking"]["link_type"] == "relates to"

        multiple_links_data = [self.LINKING_TEST_DATA[1]]
        xml_content = self._convert_to_xml_with_linking(multiple_links_data)

        with patch("builtins.open", mock_open(read_data=xml_content)):
            with patch("os.path.exists", return_value=True):
                loader = XmlFileLoader()
                issues = loader.load_issues("test.xml")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], list)
                assert len(issue["linking"]) == 2
                assert issue["linking"][0]["target_key"] == "PROJ-123"
                assert issue["linking"][0]["link_type"] == "relates to"
                assert issue["linking"][1]["target_key"] == "PROJ-456"
                assert issue["linking"][1]["link_type"] == "blocks"

    def test_json_loader_with_invalid_linking(self):
        invalid_data = [
            {
                "project": {"key": "PROJ"},
                "summary": "Task with invalid linking",
                "issuetype": {"name": "Task"},
                "linking": {"link_type": "relates to"},
            }
        ]
        json_content = json.dumps(invalid_data, ensure_ascii=False, indent=2)

        with patch("builtins.open", mock_open(read_data=json_content)):
            with patch("os.path.exists", return_value=True):
                loader = JsonFileLoader()
                issues = loader.load_issues("test.json")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], dict)
                assert "target_key" not in issue["linking"]
                assert issue["linking"]["link_type"] == "relates to"

        invalid_data = [
            {
                "project": {"key": "PROJ"},
                "summary": "Task with invalid linking",
                "issuetype": {"name": "Task"},
                "linking": {"target_key": "PROJ-123"},
            }
        ]
        json_content = json.dumps(invalid_data, ensure_ascii=False, indent=2)

        with patch("builtins.open", mock_open(read_data=json_content)):
            with patch("os.path.exists", return_value=True):
                loader = JsonFileLoader()
                issues = loader.load_issues("test.json")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], dict)
                assert issue["linking"]["target_key"] == "PROJ-123"
                assert "link_type" not in issue["linking"]

        invalid_data = [
            {
                "project": {"key": "PROJ"},
                "summary": "Task with empty linking",
                "issuetype": {"name": "Task"},
                "linking": {},
            }
        ]
        json_content = json.dumps(invalid_data, ensure_ascii=False, indent=2)

        with patch("builtins.open", mock_open(read_data=json_content)):
            with patch("os.path.exists", return_value=True):
                loader = JsonFileLoader()
                issues = loader.load_issues("test.json")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], dict)
                assert len(issue["linking"]) == 0

    def test_yaml_loader_with_invalid_linking(self):
        invalid_data = [
            {
                "project": {"key": "PROJ"},
                "summary": "Task with invalid linking",
                "issuetype": {"name": "Task"},
                "linking": {"link_type": "relates to"},
            }
        ]
        yaml_content = yaml.dump(invalid_data, allow_unicode=True)

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("os.path.exists", return_value=True):
                loader = YamlFileLoader()
                issues = loader.load_issues("test.yaml")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], dict)
                assert "target_key" not in issue["linking"]
                assert issue["linking"]["link_type"] == "relates to"

    def test_csv_loader_with_invalid_linking(self):
        mock_reader = MagicMock()
        mock_reader.fieldnames = [
            "project.key",
            "summary",
            "issuetype.name",
            "linking.link_type",
        ]
        mock_reader.__iter__ = Mock(
            return_value=iter(
                [
                    {
                        "project.key": "PROJ",
                        "summary": "Task with invalid linking",
                        "issuetype.name": "Task",
                        "linking.link_type": "relates to",
                    }
                ]
            )
        )

        with patch("builtins.open", mock_open(read_data="")):
            with patch("os.path.exists", return_value=True):
                with patch("csv.DictReader", return_value=mock_reader):
                    with patch("csv.Sniffer.sniff") as mock_sniffer:
                        mock_dialect = csv.excel()
                        mock_dialect.delimiter = ","
                        mock_sniffer.return_value = mock_dialect

                        loader = CsvFileLoader()
                        issues = loader.load_issues("test.csv")

                        assert len(issues) == 1
                        issue = issues[0]
                        assert "linking" in issue
                        assert isinstance(issue["linking"], dict)
                        assert "target_key" not in issue["linking"]
                        assert issue["linking"]["link_type"] == "relates to"

        mock_reader = MagicMock()
        mock_reader.fieldnames = [
            "project.key",
            "summary",
            "issuetype.name",
            "linking.target_key",
        ]
        mock_reader.__iter__ = Mock(
            return_value=iter(
                [
                    {
                        "project.key": "PROJ",
                        "summary": "Task with invalid linking",
                        "issuetype.name": "Task",
                        "linking.target_key": "PROJ-123",
                    }
                ]
            )
        )

        with patch("builtins.open", mock_open(read_data="")):
            with patch("os.path.exists", return_value=True):
                with patch("csv.DictReader", return_value=mock_reader):
                    with patch("csv.Sniffer.sniff") as mock_sniffer:
                        mock_dialect = csv.excel()
                        mock_dialect.delimiter = ","
                        mock_sniffer.return_value = mock_dialect

                        loader = CsvFileLoader()
                        issues = loader.load_issues("test.csv")

                        assert len(issues) == 1
                        issue = issues[0]
                        assert "linking" in issue
                        assert isinstance(issue["linking"], dict)
                        assert issue["linking"]["target_key"] == "PROJ-123"
                        assert "link_type" not in issue["linking"]

    def test_excel_loader_with_invalid_linking(self):
        from unittest.mock import MagicMock

        mock_sheet = MagicMock()
        mock_sheet.max_row = 2
        mock_sheet.max_column = 5

        cell_values = {
            (1, 1): "project.key",
            (1, 2): "summary",
            (1, 3): "issuetype.name",
            (1, 4): "linking.link_type",
        }

        cell_values[(2, 1)] = "PROJ"
        cell_values[(2, 2)] = "Task with invalid linking"
        cell_values[(2, 3)] = "Task"
        cell_values[(2, 4)] = "relates to"

        mock_sheet.cell.side_effect = lambda row, column: MagicMock(
            value=cell_values.get((row, column), None)
        )

        mock_workbook = MagicMock()
        mock_workbook.active = mock_sheet
        mock_workbook.close = MagicMock()

        with patch("os.path.exists", return_value=True):
            with patch(
                "tirajira.file_loaders.excel_loader.load_workbook",
                return_value=mock_workbook,
            ):
                with patch.object(ExcelFileLoader, "_validate_and_open_file"):
                    loader = ExcelFileLoader()
                    issues = loader.load_issues("test.xlsx")

                    assert len(issues) == 1
                    issue = issues[0]
                    assert "linking" in issue
                    assert isinstance(issue["linking"], dict)
                    assert "target_key" not in issue["linking"]
                    assert issue["linking"]["link_type"] == "relates to"

    def test_xml_loader_with_invalid_linking(self):
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<issues>
    <issue>
        <project>
            <key>PROJ</key>
        </project>
        <summary>Task with invalid linking</summary>
        <issuetype>
            <name>Task</name>
        </issuetype>
        <linking>
            <link_type>relates to</link_type>
        </linking>
    </issue>
</issues>"""

        with patch("builtins.open", mock_open(read_data=xml_content)):
            with patch("os.path.exists", return_value=True):
                loader = XmlFileLoader()
                issues = loader.load_issues("test.xml")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], dict)
                assert "target_key" not in issue["linking"]
                assert issue["linking"]["link_type"] == "relates to"

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<issues>
    <issue>
        <project>
            <key>PROJ</key>
        </project>
        <summary>Task with invalid linking</summary>
        <issuetype>
            <name>Task</name>
        </issuetype>
        <linking>
            <target_key>PROJ-123</target_key>
        </linking>
    </issue>
</issues>"""

        with patch("builtins.open", mock_open(read_data=xml_content)):
            with patch("os.path.exists", return_value=True):
                loader = XmlFileLoader()
                issues = loader.load_issues("test.xml")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], dict)
                assert issue["linking"]["target_key"] == "PROJ-123"
                assert "link_type" not in issue["linking"]

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<issues>
    <issue>
        <project>
            <key>PROJ</key>
        </project>
        <summary>Task with empty linking</summary>
        <issuetype>
            <name>Task</name>
        </issuetype>
        <linking>
        </linking>
    </issue>
</issues>"""

        with patch("builtins.open", mock_open(read_data=xml_content)):
            with patch("os.path.exists", return_value=True):
                loader = XmlFileLoader()
                issues = loader.load_issues("test.xml")

                assert len(issues) == 1
                issue = issues[0]
                assert "linking" in issue
                assert isinstance(issue["linking"], dict)
                assert len(issue["linking"]) == 0
