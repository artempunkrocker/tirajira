import os
import sys

# Добавляем корневую директорию проекта и папку src в sys.path для импорта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
