'''ComfyUI-Tabularize: Automatic node column organization'''

# Import api module to register routes
from . import api  # noqa: F401

__version__ = '0.4.0'

# Required for ComfyUI to load this custom node package
NODE_CLASS_MAPPINGS = {}

# Web extensions directory
WEB_DIRECTORY = './web'

print( '[Tabularize] Python module loaded successfully' )

__all__ = ['NODE_CLASS_MAPPINGS', 'WEB_DIRECTORY']
