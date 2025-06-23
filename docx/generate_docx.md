Markdown

# Інструкція з Генерації Документації

Ця інструкція допоможе вам згенерувати HTML-документацію для вашого проекту за допомогою Sphinx.

---
## 1. Передумови

Перш ніж почати, переконайтеся, що у вас встановлені **Python**, **Sphinx** та всі необхідні бібліотеки для вашої гри (наприклад, **Pygame**).

---
## 2. Структура Каталогів


pyga/
├── platformer.py         # основний файл з кодом гри
└── docx/                 # Кореневий каталог документації Sphinx
├── conf.py               # Файл конфігурації Sphinx
├── index.rst             # Головний файл документації
├── api.rst               # Файл для документації API (автоматично генерується з коду)
├── usage.rst             # Файл для інструкцій з використання
├── contributing.rst      # Файл для інструкцій щодо внесків
├── _templates/           # (Можливо, порожній або містить шаблони)
├── _static/              # (Можливо, порожній або містить статичні файли CSS/JS)
└── build/                # Сюди Sphinx генеруватиме HTML-файли (буде створено автоматично)


**Важливо**: Переконайтеся, що всі ваші файли `.rst` (`index.rst`, `api.rst`, `usage.rst`, `contributing.rst`) знаходяться безпосередньо в каталозі `docx/`.

---
## 3. Перевірка `conf.py`

Відкрийте файл `docx/conf.py` та переконайтеся, що він містить наступні ключові налаштування:

1.  **Шлях до вашого коду (`platformer.py`)**:
    ```python
    import os
    import sys
    sys.path.insert(0, os.path.abspath('D:/pyga')) # Вказує на кореневий каталог pyga/
    ```
    * **Примітка**: Якщо ваш `platformer.py` знаходиться в іншій підпапці всередині `pyga/` (наприклад, `pyga/src/`), тоді шлях має бути `os.path.abspath('../src')`.

2.  **Заглушки для імпортів (якщо потрібно)**:
    Якщо ваш код використовує бібліотеки, які важко імпортувати під час збірки Sphinx (як-от Pygame, що завантажує ресурси під час імпорту), використовуйте заглушки:
    ```python
    from unittest.mock import Mock

    class MockedModules(Mock):
        __all__ = []
        def __getattr__(self, name):
            return MockedModules()

    MOCK_MODULES = [
        'pygame', 'pygame.locals', 'pygame.mixer' # Додайте сюди інші проблемні імпорти, якщо вони є
    ]
    sys.modules.update((mod_name, MockedModules()) for mod_name in MOCK_MODULES)
    autodoc_mock_imports = MOCK_MODULES
    ```

3.  **Розширення Sphinx**:
    ```python
    extensions = [
        'sphinx.ext.autodoc',    # Для автоматичної документації коду
        'sphinx.ext.napoleon',   # Для підтримки docstrings у стилях Google/NumPy
    ]
    ```

---
## 4. Документування Коду (Docstrings)

Щоб розділ API генерувався автоматично, ваш Python-код (`platformer.py`) повинен містити *документаційні рядки (docstrings)** для класів, методів і функцій.

**Приклад**:

```python
class Player:
    """
    Представляє гравця у платформері.

    Відповідає за переміщення, анімацію та взаємодію.
    """
    def __init__(self, x, y):
        """
        Ініціалізує нового гравця.

        :param x: Початкова координата X.
        :type x: int
        :param y: Початкова координата Y.
        :type y: int
        """