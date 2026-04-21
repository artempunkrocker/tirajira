"""
CLI интерфейс для TiraJira.
"""

import argparse
import sys

from .extract_failed import ExtractFailedCommand
from .import_cmd import ImportCommand
from .resume import ResumeCommand


def create_argument_parser():
    """Создает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="tirajira",
        description="Инструмент для автоматизации массового создания задач в Jira",
    )

    # Добавляем общие аргументы
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    # Создаем подпарсеры для команд
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Подпарсер для команды import
    import_parser = subparsers.add_parser(
        "import", help="Импорт и создание задач из файла"
    )
    import_parser.add_argument("file", help="Путь к файлу с задачами")
    import_parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=10,
        help="Размер пакета для обработки задач (по умолчанию: 10)",
    )
    import_parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=1.0,
        help="Задержка между пакетами в секундах (по умолчанию: 1.0)",
    )
    import_parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Прекратить обработку при возникновении ошибки",
    )
    import_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Включить подробный режим логирования",
    )
    import_parser.add_argument(
        "--report",
        nargs="?",
        const=True,
        help="Сохранить машинночитаемый отчет о выполнении в формате JSON, "
        "CSV, Excel или YAML",
    )

    # Подпарсер для команды extract-failed
    extract_failed_parser = subparsers.add_parser(
        "extract-failed", help="Извлечение неудачных задач из отчета"
    )
    extract_failed_parser.add_argument("report_file", help="Путь к файлу отчета")
    extract_failed_parser.add_argument("output_file", help="Путь к выходному файлу")

    # Подпарсер для команды resume
    resume_parser = subparsers.add_parser(
        "resume", help="Продолжение выполнения из отчета"
    )
    resume_parser.add_argument("report_file", help="Путь к файлу отчета")
    resume_parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=10,
        help="Размер пакета для обработки задач (по умолчанию: 10)",
    )
    resume_parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=1.0,
        help="Задержка между пакетами в секундах (по умолчанию: 1.0)",
    )
    resume_parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Прекратить обработку при возникновении ошибки",
    )
    resume_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Включить подробный режим логирования",
    )
    resume_parser.add_argument(
        "--report",
        nargs="?",
        const=True,
        help="Сохранить машинночитаемый отчет о выполнении в формате JSON, "
        "CSV, Excel или YAML",
    )

    return parser


def main():
    """Главная точка входа CLI."""
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.command == "import":
        command = ImportCommand(args)
        command.execute()
    elif args.command == "extract-failed":
        command = ExtractFailedCommand(args)
        command.execute()
    elif args.command == "resume":
        command = ResumeCommand(args)
        command.execute()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
