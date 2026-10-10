"""Reject throwaway / undeliverable signup addresses before sending mail."""

from __future__ import annotations

DISPOSABLE_DOMAINS = frozenset(
    {
        "10minutemail.com",
        "guerrillamail.com",
        "guerrillamail.info",
        "mailinator.com",
        "mailinator.net",
        "tempmail.com",
        "temp-mail.org",
        "throwawaymail.com",
        "trashmail.com",
        "yopmail.com",
        "yopmail.fr",
        "sharklasers.com",
        "getnada.com",
        "moakt.com",
        "dispostable.com",
        "fakeinbox.com",
        "maildrop.cc",
        "inboxkitten.com",
        "guerrillamailblock.com",
    }
)

UNDELIVERABLE_TLDS = frozenset({"local", "localhost", "invalid", "internal"})


def email_signup_error(email: str) -> str | None:
    value = email.strip().lower()
    if "@" not in value:
        return "Please enter a valid email address."
    local, _, domain = value.rpartition("@")
    if not local or not domain or "." not in domain:
        return "Please enter a valid email address that can receive mail."
    if domain.startswith(".") or domain.endswith(".") or ".." in domain:
        return "Please enter a valid email address that can receive mail."
    tld = domain.rsplit(".", 1)[-1]
    if tld in UNDELIVERABLE_TLDS:
        return "Use a real email account that can receive a confirmation message."
    if domain in DISPOSABLE_DOMAINS:
        return "Temporary or disposable email addresses cannot be used to register."
    return None
