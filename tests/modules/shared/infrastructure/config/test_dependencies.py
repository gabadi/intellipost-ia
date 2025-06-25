"""Unit tests for dependency injection."""

import pytest

from infrastructure.config.dependencies import (
    DependencyContainer,
    get_settings,
)
from infrastructure.config.settings import Settings


class TestDependencyContainer:
    """Test cases for dependency container."""

    def test_container_initialization(self):
        """Test container initializes with None values."""
        container = DependencyContainer()

        assert container._user_repository is None
        assert container._product_repository is None
        assert container._ai_content_service is None
        assert container._mercadolibre_service is None
        assert container._email_service is None

    def test_register_and_get_user_repository(self):
        """Test registering and getting user repository."""
        container = DependencyContainer()
        mock_repo = object()

        container.register_user_repository(mock_repo)
        assert container.get_user_repository() is mock_repo

    def test_register_and_get_product_repository(self):
        """Test registering and getting product repository."""
        container = DependencyContainer()
        mock_repo = object()

        container.register_product_repository(mock_repo)
        assert container.get_product_repository() is mock_repo

    def test_register_and_get_ai_content_service(self):
        """Test registering and getting AI content service."""
        container = DependencyContainer()
        mock_service = object()

        container.register_ai_content_service(mock_service)
        assert container.get_ai_content_service() is mock_service

    def test_register_and_get_mercadolibre_service(self):
        """Test registering and getting MercadoLibre service."""
        container = DependencyContainer()
        mock_service = object()

        container.register_mercadolibre_service(mock_service)
        assert container.get_mercadolibre_service() is mock_service

    def test_register_and_get_email_service(self):
        """Test registering and getting email service."""
        container = DependencyContainer()
        mock_service = object()

        container.register_email_service(mock_service)
        assert container.get_email_service() is mock_service

    def test_get_unregistered_repository_raises_error(self):
        """Test that getting unregistered repository raises error."""
        container = DependencyContainer()

        with pytest.raises(RuntimeError, match="User repository not registered"):
            container.get_user_repository()

    def test_get_unregistered_service_raises_error(self):
        """Test that getting unregistered service raises error."""
        container = DependencyContainer()

        with pytest.raises(RuntimeError, match="AI content service not registered"):
            container.get_ai_content_service()


class TestDependencyFunctions:
    """Test cases for dependency functions."""

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)
