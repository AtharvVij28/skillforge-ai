"""Reusable SkillForge transactional email templates. Never include secrets or passwords."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape


@dataclass(frozen=True)
class EmailContent:
    subject: str
    html_body: str
    text_body: str


def first_name(full_name: str | None) -> str:
    parts = (full_name or "").strip().split()
    return parts[0] if parts else "there"


def performance_label(score: float) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Strong"
    if score >= 50:
        return "Developing"
    return "Needs more practice"


def _button(label: str, url: str) -> str:
    safe_url = escape(url, quote=True)
    safe_label = escape(label)
    return (
        '<p style="margin:24px 0 8px;">'
        f'<a href="{safe_url}" style="display:inline-block;background:#0b1f3a;color:#ffffff;'
        "text-decoration:none;padding:12px 20px;border-radius:6px;font-weight:600;"
        f'font-size:14px;">{safe_label}</a></p>'
    )


def _wrap(*, heading: str, inner_html: str, inner_text: str, footer_note: str | None = None) -> tuple[str, str]:
    note = footer_note or "This is a transactional message from SkillForge AI."
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(heading)}</title>
</head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1f2933;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f6f8;padding:24px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background:#ffffff;border:1px solid:#d9e2ec;border-radius:12px;">
          <tr>
            <td style="background:#0b1f3a;color:#ffffff;padding:20px 24px;border-radius:12px 12px 0 0;">
              <p style="margin:0;font-size:12px;letter-spacing:0.12em;text-transform:uppercase;opacity:0.8;">SkillForge AI</p>
              <h1 style="margin:8px 0 0;font-size:22px;line-height:1.3;">{escape(heading)}</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:24px;font-size:15px;line-height:1.6;">{inner_html}</td>
          </tr>
          <tr>
            <td style="padding:0 24px 24px;font-size:12px;color:#627d98;">{escape(note)}</td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    text = inner_text.strip() + f"\n\n—\nSkillForge AI Team\n{note}\n"
    return html, text


def _card(rows: list[tuple[str, str]]) -> str:
    items = "".join(
        f'<tr><td style="padding:6px 0;color:#627d98;width:42%;">{escape(label)}</td>'
        f'<td style="padding:6px 0;font-weight:600;">{escape(value)}</td></tr>'
        for label, value in rows
        if value
    )
    if not items:
        return ""
    return (
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" '
        'style="margin:16px 0;background:#f8fafc;border:1px solid:#e4e7eb;border-radius:8px;">'
        f'<tr><td style="padding:12px 16px;"><table width="100%">{items}</table></td></tr></table>'
    )


def welcome_email(*, full_name: str, app_url: str | None) -> EmailContent:
    name = first_name(full_name)
    subject = "Welcome to SkillForge AI 🚀"
    cta = _button("Open SkillForge AI", app_url) if app_url else ""
    inner_html = f"""
      <p>Hi {escape(name)},</p>
      <p>Welcome to SkillForge AI! Your account has been successfully created.</p>
      <p>SkillForge AI helps you build a personalized learning journey by:</p>
      <ul>
        <li>Understanding your skills and competencies</li>
        <li>Identifying skill gaps</li>
        <li>Recommending relevant learning resources</li>
        <li>Assessing your progress</li>
        <li>Continuously adapting your learning path</li>
      </ul>
      <p>Your next step: complete your profile and select the subjects you want to learn.</p>
      {cta}
      <p>Your learning journey starts now.</p>
      <p>Best,<br />SkillForge AI Team</p>
    """
    text_lines = [
        f"Hi {name},",
        "",
        "Welcome to SkillForge AI!",
        "",
        "Your account has been successfully created.",
        "",
        "SkillForge AI helps you build a personalized learning journey by:",
        "• Understanding your skills and competencies",
        "• Identifying skill gaps",
        "• Recommending relevant learning resources",
        "• Assessing your progress",
        "• Continuously adapting your learning path",
        "",
        "Your next step: complete your profile and select the subjects you want to learn.",
    ]
    if app_url:
        text_lines.extend(["", f"Open SkillForge AI: {app_url}"])
    text_lines.extend(["", "Your learning journey starts now.", "", "Best,", "SkillForge AI Team"])
    html, text = _wrap(heading=subject, inner_html=inner_html, inner_text="\n".join(text_lines))
    return EmailContent(subject=subject, html_body=html, text_body=text)


def password_reset_email(*, full_name: str, reset_url: str, expiry_minutes: int) -> EmailContent:
    name = first_name(full_name)
    subject = "Reset your SkillForge AI password"
    inner_html = f"""
      <p>Hi {escape(name)},</p>
      <p>We received a request to reset your SkillForge AI password.</p>
      {_button("Reset Password", reset_url)}
      <p>This link will expire in {int(expiry_minutes)} minutes.</p>
      <p>If you did not request a password reset, you can safely ignore this email.</p>
      <p>For your security, never share this reset link with anyone.</p>
      <p>Best,<br />SkillForge AI Team</p>
    """
    text = (
        f"Hi {name},\n\n"
        "We received a request to reset your SkillForge AI password.\n\n"
        f"Reset Password: {reset_url}\n\n"
        f"This link will expire in {int(expiry_minutes)} minutes.\n\n"
        "If you did not request a password reset, you can safely ignore this email.\n"
        "For your security, never share this reset link with anyone.\n\n"
        "Best,\nSkillForge AI Team"
    )
    html, text_body = _wrap(heading=subject, inner_html=inner_html, inner_text=text)
    return EmailContent(subject=subject, html_body=html, text_body=text_body)


def learning_recommendation_email(
    *,
    full_name: str,
    learning_title: str | None = None,
    recommendation_reason: str | None = None,
    competency_name: str | None = None,
    current_level: str | None = None,
    target_level: str | None = None,
    estimated_duration: str | None = None,
    next_action: str | None = None,
    learning_url: str | None = None,
) -> EmailContent:
    name = first_name(full_name)
    subject = "Your SkillForge AI learning recommendation 📚"
    rows = [
        ("Recommended learning", learning_title or ""),
        ("Related skill", competency_name or ""),
        ("Current level", current_level or ""),
        ("Target level", target_level or ""),
        ("Estimated learning time", estimated_duration or ""),
    ]
    reason_html = (
        f"<p><strong>Why this was recommended</strong><br />{escape(recommendation_reason)}</p>"
        if recommendation_reason
        else ""
    )
    next_html = f"<p><strong>What you can do next</strong><br />{escape(next_action)}</p>" if next_action else ""
    cta = _button("Start Learning", learning_url) if learning_url else ""
    inner_html = f"""
      <p>Hi {escape(name)},</p>
      <p>Based on your current competency profile, SkillForge AI has identified a learning opportunity for you.</p>
      {_card(rows)}
      {reason_html}
      {next_html}
      {cta}
      <p>Keep building your skills step by step.</p>
      <p>Best,<br />SkillForge AI Team</p>
    """
    text_lines = [
        f"Hi {name},",
        "",
        "Based on your current competency profile, SkillForge AI has identified a learning opportunity for you.",
        "",
    ]
    for label, value in rows:
        if value:
            text_lines.append(f"{label}: {value}")
    if recommendation_reason:
        text_lines.extend(["", "Why this was recommended:", recommendation_reason])
    if next_action:
        text_lines.extend(["", "What you can do next:", next_action])
    if learning_url:
        text_lines.extend(["", f"Start Learning: {learning_url}"])
    text_lines.extend(["", "Keep building your skills step by step.", "", "Best,", "SkillForge AI Team"])
    html, text = _wrap(heading=subject, inner_html=inner_html, inner_text="\n".join(text_lines))
    return EmailContent(subject=subject, html_body=html, text_body=text)


def assessment_result_email(
    *,
    full_name: str,
    assessment_title: str | None = None,
    score: str | None = None,
    correct_answers: str | None = None,
    total_questions: str | None = None,
    performance_label_text: str | None = None,
    competency_name: str | None = None,
    result_summary: str | None = None,
    next_step: str | None = None,
    results_url: str | None = None,
) -> EmailContent:
    name = first_name(full_name)
    subject = "Your SkillForge AI assessment results 📊"
    correct_line = ""
    if correct_answers and total_questions:
        correct_line = f"{correct_answers} / {total_questions}"
    elif correct_answers:
        correct_line = correct_answers
    rows = [
        ("Assessment", assessment_title or ""),
        ("Score", f"{score}%" if score else ""),
        ("Correct answers", correct_line),
        ("Performance", performance_label_text or ""),
        ("Skill assessed", competency_name or ""),
    ]
    summary_html = (
        f"<p><strong>What this means</strong><br />{escape(result_summary)}</p>" if result_summary else ""
    )
    next_html = (
        f"<p><strong>Recommended next step</strong><br />{escape(next_step)}</p>" if next_step else ""
    )
    cta = _button("View Detailed Results", results_url) if results_url else ""
    inner_html = f"""
      <p>Hi {escape(name)},</p>
      <p>Your assessment has been completed successfully.</p>
      {_card(rows)}
      {summary_html}
      {next_html}
      {cta}
      <p>Keep learning and improving your competency profile.</p>
      <p>Best,<br />SkillForge AI Team</p>
    """
    text_lines = [f"Hi {name},", "", "Your assessment has been completed successfully.", ""]
    for label, value in rows:
        if value:
            text_lines.append(f"{label}: {value}")
    if result_summary:
        text_lines.extend(["", "What this means:", result_summary])
    if next_step:
        text_lines.extend(["", "Recommended next step:", next_step])
    if results_url:
        text_lines.extend(["", f"View Detailed Results: {results_url}"])
    text_lines.extend(["", "Keep learning and improving your competency profile.", "", "Best,", "SkillForge AI Team"])
    html, text = _wrap(heading=subject, inner_html=inner_html, inner_text="\n".join(text_lines))
    return EmailContent(subject=subject, html_body=html, text_body=text)


def verification_email(*, full_name: str, confirm_url: str) -> EmailContent:
    name = first_name(full_name)
    subject = "Confirm your SkillForge AI account"
    inner_html = f"""
      <p>Hi {escape(name)},</p>
      <p>Confirm this email address to finish creating your SkillForge AI account.</p>
      {_button("Confirm my email", confirm_url)}
      <p>This link expires in 24 hours. If you did not register, you can ignore this message.</p>
      <p>Best,<br />SkillForge AI Team</p>
    """
    text = (
        f"Hi {name},\n\n"
        "Confirm this email address to finish creating your SkillForge AI account.\n\n"
        f"{confirm_url}\n\n"
        "This link expires in 24 hours. If you did not register, you can ignore this message.\n\n"
        "Best,\nSkillForge AI Team"
    )
    html, text_body = _wrap(heading=subject, inner_html=inner_html, inner_text=text)
    return EmailContent(subject=subject, html_body=html, text_body=text_body)
