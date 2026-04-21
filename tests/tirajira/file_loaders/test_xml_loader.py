"""
Тесты для загрузчика XML файлов.
"""

from unittest.mock import mock_open, patch

import pytest

from tirajira.file_loaders.xml_loader import XmlFileLoader


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        "<issue><project><key>PROJ</key></project>"
        "<summary>Тестовая задача</summary>"
        "<description>Описание тестовой задачи</description>"
        "<issuetype><name>Task</name></issuetype></issue>"
        "<issue><project><key>PROJ2</key></project>"
        "<summary>Еще одна задача</summary>"
        "<description>Описание второй задачи</description>"
        "<issuetype><name>Bug</name></issuetype></issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_load_issues(mock_exists, mock_file):
    """Тест: загрузка задач из XML файла"""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("test.xml")

    # Проверяем результат
    assert len(issues) == 2
    assert issues[0]["project"]["key"] == "PROJ"
    assert issues[0]["summary"] == "Тестовая задача"
    assert issues[1]["project"]["key"] == "PROJ2"
    assert issues[1]["summary"] == "Еще одна задача"


@patch("builtins.open", new_callable=mock_open)
@patch("os.path.exists", return_value=False)
def test_xml_file_loader_file_not_found(mock_exists, mock_file):
    """Тест: обработка ошибки файла не найден"""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Проверяем, что выбрасывается правильное исключение
    with pytest.raises(FileNotFoundError):
        loader.load_issues("test.xml")


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='<?xml version="1.0" encoding="UTF-8"?><invalid>',
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_invalid_xml(mock_exists, mock_file):
    """Тест: обработка ошибки невалидного XML"""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Проверяем, что выбрасывается правильное исключение
    with pytest.raises(ValueError):
        loader.load_issues("test.xml")


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='<?xml version="1.0" encoding="UTF-8"?><root></root>',
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_wrong_root_element(mock_exists, mock_file):
    """Тест: обработка ошибки неправильного корневого элемента"""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Проверяем, что выбрасывается правильное исключение
    with pytest.raises(ValueError):
        loader.load_issues("test.xml")


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        '<issue id="1"><project key="PROJ"/>'
        "<summary>Test issue 1</summary>"
        "<description>Description for test issue 1</description>"
        '<issuetype name="Task"/>'
        '<assignee email="user1@example.com"/>'
        '<priority name="High"/>'
        "<customfields>"
        '<customfield id="10001" name="Business Value">High</customfield>'
        '<customfield id="10002" name="Story Points">5</customfield>'
        "</customfields></issue>"
        '<issue id="2"><project key="PROJ"/>'
        "<summary>Test issue 2</summary>"
        "<description>Description for test issue 2</description>"
        '<issuetype name="Bug"/>'
        '<assignee email="user2@example.com"/>'
        '<priority name="Medium"/>'
        "<customfields>"
        '<customfield id="10001" name="Business Value">Medium</customfield>'
        '<customfield id="10002" name="Story Points">3</customfield>'
        "</customfields></issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_complex_structure(mock_exists, mock_file):
    """Тест: загрузка XML файла со сложной структурой."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("complex.xml")

    # Проверяем результат
    assert len(issues) == 2

    # Проверяем первую задачу
    issue1 = issues[0]
    assert issue1["project"]["key"] == "PROJ"
    assert issue1["summary"] == "Test issue 1"
    assert issue1["description"] == "Description for test issue 1"
    assert issue1["issuetype"]["name"] == "Task"
    assert issue1["assignee"]["emailAddress"] == "user1@example.com"
    assert issue1["priority"]["name"] == "High"
    assert issue1["customfield_10001"] == "High"
    assert issue1["customfield_10002"] == "5"

    # Проверяем вторую задачу
    issue2 = issues[1]
    assert issue2["project"]["key"] == "PROJ"
    assert issue2["summary"] == "Test issue 2"
    assert issue2["description"] == "Description for test issue 2"
    assert issue2["issuetype"]["name"] == "Bug"
    assert issue2["assignee"]["emailAddress"] == "user2@example.com"
    assert issue2["priority"]["name"] == "Medium"
    assert issue2["customfield_10001"] == "Medium"
    assert issue2["customfield_10002"] == "3"


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        '<issue><project key="PROJ"/>'
        "<summary>Test issue</summary>"
        "<description>Description</description>"
        '<issuetype name="Task"/>'
        "<customfields>"
        '<customfield id="customfield_10001" name="Business Value">High</customfield>'
        "</customfields></issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_dot_notation(mock_exists, mock_file):
    """Тест: обработка dot notation в атрибутах."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("dot_notation.xml")

    # Проверяем результат
    assert len(issues) == 1
    issue = issues[0]
    assert "customfield_10001" in issue
    assert issue["customfield_10001"] == "High"


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        '<issue><project key="PROJ"/>'
        "<summary>Test issue</summary>"
        "<description>Description</description>"
        '<issuetype name="Task"/>'
        "<labels><label>urgent</label><label>backend</label></labels>"
        "</issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_merge_dicts(mock_exists, mock_file):
    """Тест: объединение словарей."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("merge_dicts.xml")

    # Проверяем результат
    assert len(issues) == 1
    issue = issues[0]
    assert "labels" in issue
    assert isinstance(issue["labels"], list)
    assert "urgent" in issue["labels"]
    assert "backend" in issue["labels"]


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        '<issue><project key="PROJ"/>'
        "<summary>Simple text content</summary>"
        "</issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_element_to_dict_text_content(mock_exists, mock_file):
    """Тест: преобразование элемента с текстовым содержимым в словарь."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("text_content.xml")

    # Проверяем результат
    assert len(issues) == 1
    issue = issues[0]
    assert issue["summary"] == "Simple text content"


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        '<issue><project key="PROJ"/>'
        "<summary>Mixed <b>bold</b> and <i>italic</i> content</summary>"
        "</issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_element_to_dict_mixed_content(mock_exists, mock_file):
    """Тест: преобразование элемента со смешанным содержимым в словарь."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("mixed_content.xml")

    # Проверяем результат
    assert len(issues) == 1
    issue = issues[0]
    # Текстовое содержимое элемента со смешанным содержимым должно быть объединено
    assert "Mixed bold and italic content" in issue["summary"]


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        '<issue><project key="PROJ"/>'
        "<attachments>"
        '<attachment name="file1.txt"/>'
        '<attachment name="file2.pdf"/>'
        "</attachments></issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_element_to_dict_list_elements(mock_exists, mock_file):
    """Тест: преобразование элемента со списком подэлементов в словарь."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("list_elements.xml")

    # Проверяем результат
    assert len(issues) == 1
    issue = issues[0]
    assert "attachments" in issue
    assert isinstance(issue["attachments"], list)
    assert len(issue["attachments"]) == 2
    assert issue["attachments"][0]["name"] == "file1.txt"
    assert issue["attachments"][1]["name"] == "file2.pdf"


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        '<issue><project key="PROJ"/>'
        "<summary>Test with attributes</summary>"
        '<customfield id="10001">Value1</customfield>'
        '<customfield id="10002">Value2</customfield>'
        "</issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_custom_fields_processing(mock_exists, mock_file):
    """Тест: обработка custom fields."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("custom_fields.xml")

    # Проверяем результат
    assert len(issues) == 1
    issue = issues[0]
    assert "customfield_10001" in issue
    assert issue["customfield_10001"] == "Value1"
    assert "customfield_10002" in issue
    assert issue["customfield_10002"] == "Value2"


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        '<issue><project key="PROJ"/>'
        "<summary>Test with nested elements</summary>"
        '<assignee email="test@example.com" name="Test User"/>'
        '<priority name="High"/>'
        "</issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_nested_elements_with_attributes(mock_exists, mock_file):
    """Тест: обработка вложенных элементов с атрибутами."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("nested_elements.xml")

    # Проверяем результат
    assert len(issues) == 1
    issue = issues[0]
    assert issue["assignee"]["emailAddress"] == "test@example.com"
    assert issue["assignee"]["name"] == "Test User"
    assert issue["priority"]["name"] == "High"


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        '<issue><project key="PROJ"/>'
        "<summary>Description<b>bold</b> and <i>italic</i> text</summary>"
        "</issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_mixed_content_with_tail(mock_exists, mock_file):
    """Тест: обработка элементов со смешанным содержимым и текстом после
    дочерних элементов."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("mixed_content_tail.xml")

    # Проверяем результат
    assert len(issues) == 1
    issue = issues[0]
    # Проверяем, что текстовое содержимое правильно объединено
    summary = issue["summary"]
    assert isinstance(summary, str)
    assert "Description" in summary
    assert "bold" in summary
    assert "and" in summary
    assert "italic" in summary
    assert "text" in summary


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        '<issue><project key="PROJ"/>'
        "<empty_element></empty_element>"
        "<whitespace_element>   </whitespace_element>"
        "</issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_empty_and_whitespace_elements(mock_exists, mock_file):
    """Тест: обработка пустых элементов и элементов с пробелами."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("empty_whitespace.xml")

    # Проверяем результат
    assert len(issues) == 1
    issue = issues[0]
    # Пустые элементы должны быть представлены как пустые строки
    assert issue["empty_element"] == ""
    # Элементы с пробелами должны быть очищены
    assert issue["whitespace_element"] == ""


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        '<?xml version="1.0" encoding="UTF-8"?><issues>'
        "<issue><project.key>PROJ</project.key>"
        "<summary>Dot notation in element names</summary>"
        "</issue></issues>"
    ),
)
@patch("os.path.exists", return_value=True)
def test_xml_file_loader_dot_notation_in_element_names(mock_exists, mock_file):
    """Тест: обработка точечной нотации в именах элементов."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Загружаем задачи
    issues = loader.load_issues("dot_notation_elements.xml")

    # Проверяем результат
    assert len(issues) == 1
    issue = issues[0]
    # Элементы с точечной нотацией должны быть преобразованы в вложенные словари
    assert "project" in issue
    assert isinstance(issue["project"], dict)
    assert "key" in issue["project"]
    assert issue["project"]["key"] == "PROJ"


def test_xml_file_loader_merge_dicts_logic():
    """Тест: логика объединения словарей в _merge_dicts методе."""
    # Создаем загрузчик
    loader = XmlFileLoader()

    # Тестируем объединение двух простых словарей
    target = {"a": 1, "b": 2}
    source = {"b": 3, "c": 4}
    loader._merge_dicts(target, source)
    assert target == {"a": 1, "b": [2, 3], "c": 4}

    # Тестируем объединение вложенных словарей
    target = {"a": {"x": 1}, "b": 2}
    source = {"a": {"y": 2}, "c": 3}
    loader._merge_dicts(target, source)
    assert target == {"a": {"x": 1, "y": 2}, "b": 2, "c": 3}

    # Тестируем добавление к существующему списку
    target = {"a": [1, 2]}
    source = {"a": 3}
    loader._merge_dicts(target, source)
    assert target == {"a": [1, 2, 3]}
