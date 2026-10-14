"""ARGUS profiles - sovereign vs institutional behaviour presets.

The core stays single-source. A profile only selects which modes,
gated keywords and verify requirements are active. Default profile
is sovereign to keep backward compatibility.
"""
from __future__ import annotations

SOVEREIGN_MODES = [
    "quick",
    "compare",
    "deep",
    "platform",
    "timeboxed",
    "regional",
    "narrow",
]

INSTITUTIONAL_MODES = ["quick", "compare", "regional"]

SOVEREIGN_PROFILE: dict = {
    "name": "sovereign",
    "allowed_modes": list(SOVEREIGN_MODES),
    "default_mode": "deep",
    "gated_keywords": {
        "scraping": ["scrape", "scraping", "crawl", "crawling", "scraper"],
        "forums": ["reddit", "forum", "community", "telegram"],
        "dark": ["dark web", "darknet", "tor network"],
        "restricted": ["login", "paywall", "captcha", "bypass"],
    },
    "require_consent_log": True,
    "verify_checks": ["structure", "urls", "citations", "languages", "consent-log"],
    "description": "Full research power with explicit consent gates.",
}

INSTITUTIONAL_PROFILE: dict = {
    "name": "institutional",
    "allowed_modes": list(INSTITUTIONAL_MODES),
    "default_mode": "quick",
    "gated_keywords": {
        "scraping": [],
        "forums": [],
        "dark": [],
        "restricted": [],
    },
    "require_consent_log": False,
    "verify_checks": ["structure", "urls"],
    "description": "Light institutional preset for admin and academic use.",
}

PROFILES: dict[str, dict] = {
    "sovereign": SOVEREIGN_PROFILE,
    "institutional": INSTITUTIONAL_PROFILE,
}


def get_profile(name: str | None = None) -> dict:
    """Return the profile dict for name, defaulting to sovereign."""
    if not name:
        return SOVEREIGN_PROFILE
    key = str(name).strip().lower()
    return PROFILES.get(key, SOVEREIGN_PROFILE)


def allowed_modes(name: str | None = None) -> list[str]:
    """Allowed mode keys for the given profile name."""
    return list(get_profile(name)["allowed_modes"])


def default_mode(name: str | None = None) -> str:
    """Default fallback mode for the given profile name."""
    return str(get_profile(name)["default_mode"])


def require_consent_log(name: str | None = None) -> bool:
    """Whether verify must require a consent log for the profile."""
    return bool(get_profile(name)["require_consent_log"])
