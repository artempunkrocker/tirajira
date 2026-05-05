"""
Loader for issues from XML files.
"""

import xml.etree.ElementTree as ET
from typing import Any, Dict, List
from xml.etree.ElementTree import Element

from ..utils.dot_notation_utils import convert_dot_notation_to_nested_dict
from .base_loader import BaseFileLoader
from .exception_handler import handle_loader_exceptions


def _get_element_text_with_children(element: Element) -> str:
    """
    Gets text content of an element with all nested elements.

    Args:
        element: XML element

    Returns:
        Text content of the element
    """
    # Start with text before first child element
    text_parts = [element.text or ""]

    # Add text from all child elements
    for child in element:
        # Add child element text
        text_parts.append(child.text or "")
        # Add text after child element
        text_parts.append(child.tail or "")

    # Join all parts and remove extra spaces
    return "".join(text_parts).strip()


class XmlFileLoader(BaseFileLoader):
    """Loader for issues from XML files."""

    @handle_loader_exceptions(format_name="XML file")
    def load_issues(self, file_path: str) -> List[Dict[Any, Any]]:
        """Loads issues from XML file."""
        # Validate file path and open it
        with self._validate_and_open_file(file_path) as f:
            # Parse XML file
            tree = ET.parse(f)
            root = tree.getroot()

        # Check that root element is 'issues'
        if root.tag != "issues":
            raise ValueError("XML file must contain root element 'issues'")

        issues = []
        # Process each 'issue' element in the root element
        for issue_element in root.findall("issue"):
            issue_dict = self._element_to_dict(issue_element)
            issues.append(issue_dict)

        return issues

    def _element_to_dict(self, element: Element) -> Dict[Any, Any]:
        """
        Converts XML element to dictionary.

        Args:
            element: XML element to convert

        Returns:
            Dictionary representing XML element structure
        """
        # If element has no child elements and no attributes, return its text
        if len(element) == 0 and not element.attrib:
            text = element.text.strip() if element.text else ""
            return text

        # If element has child elements but no attributes,
        # and we want to get text with all nested elements
        if len(element) > 0 and not element.attrib:
            # Check if element contains meaningful text with mixed content
            # Ignore only whitespace text
            has_meaningful_text = element.text and element.text.strip()
            has_meaningful_tail = any(
                child.tail and child.tail.strip() for child in element
            )

            if has_meaningful_text or has_meaningful_tail:
                text = _get_element_text_with_children(element)
                return text

        result = {}

        # Process element attributes
        self._process_attributes(element, result)

        # Process child elements
        children_dict = self._process_children(element)

        # Merge children_dict with result
        self._merge_dicts(result, children_dict)

        # Post-processing for special cases
        self._post_process_result(result)

        return result

    def _process_attributes(self, element: Element, result: Dict[Any, Any]) -> None:
        """
        Processes XML element attributes.

        Args:
            element: XML element to process attributes
            result: Dictionary to store result
        """
        for key, value in element.attrib.items():
            # For special attributes, create the needed structure
            if key == "email":
                result["emailAddress"] = value
            elif key == "name":
                result["name"] = value
            elif key == "key":
                result["key"] = value
            else:
                # If key uses dot notation, parse it correctly
                if "." in key:
                    # Create temporary dictionary with one key and convert it
                    temp_dict = {key: value}
                    nested_dict = convert_dot_notation_to_nested_dict(temp_dict)
                    # Merge with result
                    self._merge_dicts(result, nested_dict)
                else:
                    result[key] = value

    def _process_children(self, element: Element) -> Dict[Any, Any]:
        """
        Processes child elements of XML element.

        Args:
            element: XML element to process child elements

        Returns:
            Dictionary with processed child elements
        """
        children_dict = {}
        # Group child elements by tag
        children_by_tag = {}
        for child in element:
            if child.tag not in children_by_tag:
                children_by_tag[child.tag] = []
            children_by_tag[child.tag].append(child)

        # Process each group of child elements
        for tag, children in children_by_tag.items():
            if tag == "customfield":
                # Special processing for customfield
                self._process_customfields(children, children_dict)
                continue

            if len(children) == 1:
                # One element - process it as a regular element
                child_dict = self._process_child_element(children[0])
                self._add_to_children_dict(tag, child_dict, children_dict)
            else:
                # Multiple elements with same tag - create list
                child_list = []
                for child in children:
                    child_dict = self._process_child_element(child)
                    child_list.append(child_dict)

                self._add_to_children_dict(tag, child_list, children_dict)

        return children_dict

    def _process_customfields(
        self, children: List[Element], children_dict: Dict[Any, Any]
    ) -> None:
        """
        Special processing for customfield elements.

        Args:
            children: List of child elements of type customfield
            children_dict: Dictionary to store result
        """
        for child in children:
            # For customfield use id as key,
            # and text as value
            id_attr = child.get("id")
            if id_attr:
                # Form correct key for customfield
                if not id_attr.startswith("customfield_"):
                    key = f"customfield_{id_attr}"
                else:
                    key = id_attr
                # Get text content of element
                text = child.text.strip() if child.text else ""
                children_dict[key] = text

    def _process_child_element(self, child: Element) -> Any:
        """
        Processes one child element.

        Args:
            child: Child element to process

        Returns:
            Result of processing child element
        """
        # If child element has child elements or attributes,
        # recursively convert it to dictionary
        if len(child) > 0 or child.attrib:
            # Check if element contains meaningful text with mixed content
            # Ignore only whitespace text
            has_meaningful_text = child.text and child.text.strip()
            has_meaningful_tail = any(ch.tail and ch.tail.strip() for ch in child)

            if has_meaningful_text or has_meaningful_tail:
                # Use _get_element_text_with_children to get
                # text with all nested elements
                return _get_element_text_with_children(child)
            else:
                return self._element_to_dict(child)
        else:
            # If child element is a text node
            # Elements that should return {} instead of ""
            special_elements = {"linking"}
            if child.tag in special_elements:
                return {}  # Return empty dictionary for special elements
            return child.text.strip() if child.text else ""

    def _add_to_children_dict(
        self, tag: str, value: Any, children_dict: Dict[Any, Any]
    ) -> None:
        """
        Adds value to children dictionary considering dot notation.

        Args:
            tag: Element tag
            value: Value to add
            children_dict: Children dictionary
        """
        # If key uses dot notation, parse it correctly
        if "." in tag:
            # Create temporary dictionary with one key and convert it
            temp_dict = {tag: value}
            nested_dict = convert_dot_notation_to_nested_dict(temp_dict)
            # Merge with children_dict
            self._merge_dicts(children_dict, nested_dict)
        else:
            children_dict[tag] = value

    def _post_process_result(self, result: Dict[Any, Any]) -> None:
        """
        Post-processing result for special cases.

        Args:
            result: Result dictionary for post-processing
        """
        # Process linking information
        self._process_list_field(result, "linking", "link")

        # Process labels
        self._process_list_field(result, "labels", "label")

        # Process attachments
        self._process_list_field(result, "attachments", "attachment")

        # Special processing for customfields - move all customfield_* to top level
        self._process_customfields_post(result)

    def _process_customfields_post(self, result: Dict[Any, Any]) -> None:
        """
        Processes customfields in result, moving customfield_* to top level.

        Args:
            result: Result dictionary for processing
        """
        if "customfields" in result:
            customfields = result.pop("customfields")
            if isinstance(customfields, dict):
                for key, value in customfields.items():
                    if key.startswith("customfield_"):
                        result[key] = value

    def _process_list_field(
        self, result: Dict[Any, Any], field_name: str, item_name: str
    ) -> None:
        """
        Processes fields that should be lists.

        Used to convert fields containing nested elements
        of the same type into lists of values. For example, converts structure
        {"labels": {"label": "bug"}} to {"labels": ["bug"]} or
        {"labels": ["bug", "frontend"]} if multiple elements.

        Args:
            result: Result dictionary for processing
            field_name: Name of field to process (e.g., "labels", "attachments")
            item_name: Name of element in field (e.g., "label", "attachment")
        """
        if (
            field_name in result
            and isinstance(result[field_name], dict)
            and item_name in result[field_name]
        ):
            item_data = result[field_name][item_name]
            if isinstance(item_data, list):
                result[field_name] = item_data
            else:
                result[field_name] = [item_data]

    def _process_labels(self, result: Dict[Any, Any]) -> None:
        """
        Processes labels in result, converting them to list.

        Converts structure {"labels": {"label": "bug"}} to {"labels": ["bug"]}
        or {"labels": ["bug", "frontend"]} if multiple labels.

        Args:
            result: Result dictionary for processing
        """
        self._process_list_field(result, "labels", "label")

    def _process_attachments(self, result: Dict[Any, Any]) -> None:
        """
        Processes attachments in result, converting them to list.

        Converts structure {"attachments": {"attachment": {"name": "file.txt"}}}
        to {"attachments": [{"name": "file.txt"}]} or list of attachments if multiple.

        Args:
            result: Result dictionary for processing
        """
        self._process_list_field(result, "attachments", "attachment")

    def _process_customfields_post(self, result: Dict[Any, Any]) -> None:
        """
        Processes customfields in result, moving them to top level.

        Converts structure {"customfields": {"customfield_10001": "Value1"}}
        to {"customfield_10001": "Value1"} by extracting all custom
        fields to top level of result dictionary.

        Args:
            result: Result dictionary for processing
        """
        # Special processing for customfields - move all customfield
        # to top level
        if "customfields" in result:
            customfields = result.pop("customfields")
            if isinstance(customfields, dict):
                for key, value in customfields.items():
                    if key.startswith("customfield_"):
                        result[key] = value

    def _merge_dicts(self, target: Dict[Any, Any], source: Dict[Any, Any]) -> None:
        """
        Recursively merges two dictionaries.

        Args:
            target: Target dictionary for merging
            source: Source data for merging
        """
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                # If both values are dictionaries, recursively merge them
                self._merge_dicts(target[key], value)
            elif key in target and isinstance(target[key], list):
                # If value in target is already a list, append to it
                target[key].append(value)
            elif key in target:
                # If key already exists, convert to list
                target[key] = [target[key], value]
            else:
                # If key doesn't exist, just add it
                target[key] = value
