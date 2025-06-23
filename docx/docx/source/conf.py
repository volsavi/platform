import os
import sys
from unittest.mock import Mock

class MockedModules(Mock):
    __all__ = [] # Це важливо для відсутності помилок про відсутність атрибутів

    def __getattr__(self, name):
        return MockedModules()

MOCK_MODULES = [
    'pygame', 'pygame.locals', 'pygame.mixer', # Додаємо всі можливі модулі Pygame
]
sys.modules.update((mod_name, MockedModules()) for mod_name in MOCK_MODULES)

autodoc_mock_imports = MOCK_MODULES
sys.path.insert(0, os.path.abspath('D:/pyga'))


project = 'platformer'
copyright = '2025, volsavi(Voloshyn O.V.)'
author = 'volsavi(Voloshyn O.V.)'
release = '1.0'


extensions = []

templates_path = ['_templates']
exclude_patterns = []

language = 'uk'


html_theme = 'alabaster'
html_static_path = ['_static']

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]