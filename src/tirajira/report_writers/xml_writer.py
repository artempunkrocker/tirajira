"""
XML report writer.
"""

import xml.etree.ElementTree as ET
from typing import Any, Dict

from .base import ReportWriter


class XmlReportWriter(ReportWriter):
    """XML report writer."""

    def write_report(self, report_data: Dict[str, Any], file_path: str) -> None:
        """
        Writes a report to an XML file.

        Args:
            report_data: Report data to write
            file_path: Path to the report file
        """
        # Create root element
        root = ET.Element("report")

        # Add metadata
        metadata_element = ET.SubElement(root, "metadata")
        self._dict_to_elements(metadata_element, report_data.get("metadata", {}))

        # Add tasks
        tasks_element = ET.SubElement(root, "tasks")
        for task in report_data.get("tasks", []):
            task_element = ET.SubElement(tasks_element, "task")
            self._dict_to_elements(task_element, task)

        # Create XML tree and write to file
        tree = ET.ElementTree(root)

        # Format XML for better readability
        self._indent(root)

        # Write to file
        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    def _dict_to_elements(self, parent: ET.Element, data: Dict[str, Any]) -> None:
        """
        Converts a dictionary to XML elements.

        Args:
            parent: Parent XML element
            data: Dictionary to convert
        """
        for key, value in data.items():
            if isinstance(value, dict):
                # For nested dictionaries, create a separate element
                element = ET.SubElement(parent, key)
                self._dict_to_elements(element, value)
            elif isinstance(value, list):
                # For lists, create a separate element for each item
                list_element = ET.SubElement(parent, key)
                for item in value:
                    if isinstance(item, dict):
                        item_element = ET.SubElement(list_element, "item")
                        self._dict_to_elements(item_element, item)
                    else:
                        item_element = ET.SubElement(list_element, "item")
                        item_element.text = str(item)
            else:
                # For simple values, create an element with text
                element = ET.SubElement(parent, key)
                element.text = str(value) if value is not None else ""

    def _indent(self, elem: ET.Element, level: int = 0) -> None:
        """
        Adds indentation for formatting XML.

        Args:
            elem: XML element to format
            level: Indentation level
        """
        indent = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent
