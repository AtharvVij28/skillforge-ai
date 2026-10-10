"""Outbound transactional email. Never logs tokens, passwords, or API keys."""

from __future__ import annotations

import hashlib
import logging
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Any, Callable
from uuid import UUID

import httpx
from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user import EmailVerificationToken, PasswordResetToken, User
from app.services import email_templates

logger = logging.getLogger(__name__)

TOKEN_TTL = timedelta(hours=24)
PASSWORD_RESET_TTL = timedelta(minutes=30)
PASSWORD_RESET_MINUTES = 30
RESEND_TEST_FROM = "SkillForge AI <onboarding@resend.dev>"


class EmailDeliveryError(Exception):
    """Raised when mail cannot be sent."""


def hash_secret_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


hash_verification_token = hash_secret_token


def frontend_base_url() -> str:
    return get_settings().frontend_public_url.rstrip("/")


def verification_link(token: str) -> str:
    return f"{frontend_base_url()}/verify-email?token={token}"


def password_reset_link(token: str) -> str:
    return f"{frontend_base_url()}/reset-password?token={token}"


def _from_address() -> str:
    settings = get_settings()
    return (settings.resend_from or settings.smtp_from or "").strip() or RESEND_TEST_FROM


def _resend_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
        message = payload.get("message") or payload.get("error")
        if isinstance(message, dict):
            message = message.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    except Exception:
        pass
    return "Resend rejected the email."


def send_email(
    to_email: str,
    subject: str,
    html_content: str | None = None,
    *,
    text_body: str | None = None,
    html_body: str | None = None,
) -> None:
    """Low-level sender. html_content is accepted as an alias for html_body."""
    settings = get_settings()
    html = (html_content or html_body or "").strip()
    text = (text_body or "").strip() or "SkillForge AI notification"
    resend_key = (settings.resend_api_key or "").strip()
    from_address = _from_address()
    if resend_key:
        try:
            payload: dict[str, Any] = {
                "from": from_address,
                "to": [to_email],
                "subject": subject,
                "text": text,
            }
            if html:
                payload["html"] = html
            response = httpx.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=20.0,
            )
            if response.is_error:
                raise EmailDeliveryError(_resend_error_message(response))
        except EmailDeliveryError:
            raise
        except Exception as exc:
            raise EmailDeliveryError("Could not reach Resend to send email.") from exc
        return

    host = (settings.smtp_host or "").strip()
    if not host:
        raise EmailDeliveryError("SMTP or Resend is not configured.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = from_address
    message["To"] = to_email
    message.set_content(text)
    if html:
        message.add_alternative(html, subtype="html")

    try:
        if int(settings.smtp_port) == 465:
            with smtplib.SMTP_SSL(host, settings.smtp_port, timeout=20) as smtp:
                username = (settings.smtp_username or "").strip()
                password = settings.smtp_password or resend_key
                if username:
                    smtp.login(username, password)
                smtp.send_message(message)
            return
        with smtplib.SMTP(host, settings.smtp_port, timeout=20) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            username = (settings.smtp_username or "").strip()
            password = settings.smtp_password or resend_key
            if username:
                smtp.login(username, password)
            smtp.send_message(message)
    except EmailDeliveryError:
        raise
    except Exception as exc:
        raise EmailDeliveryError("Could not send email.") from exc


def send_safely(kind: str, user_id: UUID | str | None, sender: Callable[[], None]) -> None:
    try:
        sender()
    except EmailDeliveryError:
        identifier = str(user_id) if user_id is not None else "unknown"
        logger.warning("%s email failed for user %s", kind, identifier)


def dispatch_email(background: BackgroundTasks | None, kind: str, user_id: UUID | str | None, sender: Callable[[], None]) -> None:
    if background is not None:
        background.add_task(send_safely, kind, user_id, sender)
        return
    send_safely(kind, user_id, sender)


def _deliver(content: email_templates.EmailContent, to_email: str) -> None:
    send_email(to_email, content.subject, content.html_body, text_body=content.text_body)


def send_welcome_email(*, to_email: str, full_name: str, user_id: UUID | str | None = None) -> None:
    app_url = frontend_base_url() or None
    content = email_templates.welcome_email(full_name=full_name, app_url=app_url)
    send_safely("Welcome", user_id, lambda: _deliver(content, to_email))


def send_password_reset_email(
    *,
    to_email: str,
    full_name: str,
    reset_token: str,
    user_id: UUID | str | None = None,
) -> None:
    content = email_templates.password_reset_email(
        full_name=full_name,
        reset_url=password_reset_link(reset_token),
        expiry_minutes=PASSWORD_RESET_MINUTES,
    )
    send_safely("Password reset", user_id, lambda: _deliver(content, to_email))


def send_learning_recommendation_email(
    *,
    to_email: str,
    full_name: str,
    user_id: UUID | str | None = None,
    learning_title: str | None = None,
    recommendation_reason: str | None = None,
    competency_name: str | None = None,
    current_level: str | None = None,
    target_level: str | None = None,
    estimated_duration: str | None = None,
    next_action: str | None = None,
    learning_url: str | None = None,
) -> None:
    content = email_templates.learning_recommendation_email(
        full_name=full_name,
        learning_title=learning_title,
        recommendation_reason=recommendation_reason,
        competency_name=competency_name,
        current_level=current_level,
        target_level=target_level,
        estimated_duration=estimated_duration,
        next_action=next_action,
        learning_url=learning_url,
    )
    send_safely("Learning recommendation", user_id, lambda: _deliver(content, to_email))


def send_assessment_result_email(
    *,
    to_email: str,
    full_name: str,
    user_id: UUID | str | None = None,
    assessment_title: str | None = None,
    score: str | None = None,
    correct_answers: str | None = None,
    total_questions: str | None = None,
    performance_label_text: str | None = None,
    competency_name: str | None = None,
    result_summary: str | None = None,
    next_step: str | None = None,
) -> None:
    content = email_templates.assessment_result_email(
        full_name=full_name,
        assessment_title=assessment_title,
        score=score,
        correct_answers=correct_answers,
        total_questions=total_questions,
        performance_label_text=performance_label_text,
        competency_name=competency_name,
        result_summary=result_summary,
        next_step=next_step,
        results_url=f"{frontend_base_url()}/assess",
    )
    send_safely("Assessment result", user_id, lambda: _deliver(content, to_email))


def send_verification_email(to_email: str, full_name: str, token: str) -> None:
    content = email_templates.verification_email(full_name=full_name, confirm_url=verification_link(token))
    _deliver(content, to_email)


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def create_verification_token(db: Session, user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    existing = db.scalars(
        select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used_at.is_(None),
        )
    ).all()
    for row in existing:
        row.used_at = now
        db.add(row)

    raw = secrets.token_urlsafe(32)
    db.add(
        EmailVerificationToken(
            user_id=user_id,
            token_hash=hash_secret_token(raw),
            expires_at=now + TOKEN_TTL,
        )
    )
    db.commit()
    return raw


def issue_and_send_verification(db: Session, user: User) -> None:
    settings = get_settings()
    if not settings.mail_delivery_configured:
        logger.warning("Verification email skipped; mail is not configured")
        return
    token = create_verification_token(db, user.id)
    try:
        send_verification_email(user.email, user.full_name, token)
    except EmailDeliveryError:
        logger.warning("Verification email failed for user %s", user.id)


def consume_verification_token(db: Session, token: str) -> User:
    if not token.strip():
        raise ValueError("Missing confirmation token")
    now = datetime.now(timezone.utc)
    row = db.scalar(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == hash_secret_token(token.strip())
        )
    )
    expires_at = _aware(row.expires_at if row is not None else None)
    if row is None or row.used_at is not None or expires_at is None or expires_at < now:
        raise ValueError("This confirmation link is invalid or has expired")
    user = db.get(User, row.user_id)
    if user is None:
        raise ValueError("This confirmation link is invalid or has expired")
    row.used_at = now
    user.email_verified_at = now
    db.add(row)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_password_reset_token(db: Session, user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    existing = db.scalars(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
        )
    ).all()
    for row in existing:
        row.used_at = now
        db.add(row)
    raw = secrets.token_urlsafe(32)
    db.add(
        PasswordResetToken(
            user_id=user_id,
            token_hash=hash_secret_token(raw),
            expires_at=now + PASSWORD_RESET_TTL,
        )
    )
    db.commit()
    return raw


def consume_password_reset_token(db: Session, token: str) -> User:
    if not token.strip():
        raise ValueError("This reset link is invalid or has expired")
    now = datetime.now(timezone.utc)
    row = db.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == hash_secret_token(token.strip()))
    )
    expires_at = _aware(row.expires_at if row is not None else None)
    if row is None or row.used_at is not None or expires_at is None or expires_at < now:
        raise ValueError("This reset link is invalid or has expired")
    user = db.get(User, row.user_id)
    if user is None:
        raise ValueError("This reset link is invalid or has expired")
    row.used_at = now
    for other in db.scalars(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
    ).all():
        other.used_at = now
        db.add(other)
    db.add(row)
    db.add(user)
    return user
