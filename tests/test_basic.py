"""
Tests for AI Research Assistant

This module contains unit and integration tests for the application.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from config import load_config, EndeeConfig, EmbeddingConfig, LLMConfig
from utils import DocumentProcessor, TextCleaner


class TestDocumentProcessor:
    """Test document processing functionality."""
    
    def test_text_cleaner_clean(self):
        """Test text cleaning."""
        text = "  This   is   a   test  \n  with   extra   spaces  "
        cleaned = TextCleaner.clean(text)
        assert "  " not in cleaned
        assert cleaned == "This is a test with extra spaces"
    
    def test_text_truncate(self):
        """Test text truncation."""
        text = "a" * 100
        truncated = TextCleaner.truncate(text, max_length=50)
        assert len(truncated) <= 50
        assert truncated.endswith("...")
    
    def test_text_truncate_short_text(self):
        """Test truncation of short text (should not truncate)."""
        text = "short"
        truncated = TextCleaner.truncate(text, max_length=50)
        assert truncated == text


class TestConfiguration:
    """Test configuration management."""
    
    def test_config_loading(self):
        """Test that configuration loads successfully."""
        config = load_config()
        assert config is not None
        assert config.endee.index_name
        assert config.embedding.model_name
        assert config.llm.model_name


if __name__ == "__main__":
    pytest.main([__file__])
