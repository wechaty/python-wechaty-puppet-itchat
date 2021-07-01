"""
doc
"""
from .puppet import PuppetService

from .version import VERSION


__version__ = VERSION

__all__ = [
    'PuppetService',

    '__version__'
]
