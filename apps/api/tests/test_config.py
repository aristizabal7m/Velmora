import pytest

from velmora.core.config import Settings


def test_cors_origins_accepts_comma_separated_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://velmora-web.vercel.app, https://velmora-web-two.vercel.app",
    )

    settings = Settings()

    assert settings.environment == "production"
    assert settings.cors_origins == [
        "https://velmora-web.vercel.app",
        "https://velmora-web-two.vercel.app",
    ]
