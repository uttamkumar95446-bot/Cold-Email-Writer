"""Tests for config.py"""

import os
import pytest
from config import Config, validate_config


class TestValidateConfig:
    def test_dry_run_requires_no_credentials(self):
        config = Config(dry_run=True)
        errors = validate_config(config)
        assert len(errors) == 0

    def test_smtp_send_requires_credentials(self):
        config = Config(dry_run=False, send_method="smtp")
        errors = validate_config(config)
        assert any("SMTP_USER" in e for e in errors)
        assert any("SMTP_PASSWORD" in e for e in errors)
        assert any("SENDER_NAME" in e for e in errors)

    def test_unknown_send_method(self):
        config = Config(send_method="unknown")
        errors = validate_config(config)
        assert any("unknown" in e.lower() for e in errors)

    def test_unusual_port_warning(self):
        config = Config(smtp_port=1234)
        errors = validate_config(config)
        assert any("Unusual" in e for e in errors)

    def test_standard_port_no_warning(self):
        config = Config(smtp_port=587)
        errors = validate_config(config)
        port_errors = [e for e in errors if "port" in e.lower()]
        assert len(port_errors) == 0


class TestConfigDefaults:
    def test_default_dry_run_is_true(self):
        config = Config()
        assert config.dry_run is True

    def test_default_send_method_is_smtp(self):
        config = Config()
        assert config.send_method == "smtp"

    def test_default_smtp_host(self):
        config = Config()
        assert config.smtp_host == "smtp.gmail.com"

    def test_default_smtp_port(self):
        config = Config()
        assert config.smtp_port == 587
