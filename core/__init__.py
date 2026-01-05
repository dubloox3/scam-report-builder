"""
Core module for Scam Report Builder
"""
from .config_manager import ConfigManager
from .template_manager import TemplateManager
from .odt_generator import ODTGenerator

__all__ = ['ConfigManager', 'TemplateManager', 'ODTGenerator']