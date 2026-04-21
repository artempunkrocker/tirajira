"""
Базовый класс для команд TiraJira.
"""


class BaseCommand:
    """Базовый класс команды."""

    def __init__(self, args):
        self.args = args

    def execute(self):
        """Выполняет команду."""
        raise NotImplementedError("Метод execute должен быть реализован в подклассе.")
