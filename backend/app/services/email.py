"""Transactional email.

Default provider is Resend. With no ``RESEND_API_KEY`` a console provider logs
the message, so the full flow runs with zero external dependencies (dev, tests,
CI). Sending is invoked from a FastAPI ``BackgroundTask`` (sync callable → runs
in the threadpool) so a slow or failing provider never blocks or fails the
prospect's submission; providers also swallow and log their own errors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger
from app.templates.email import messages

logger = get_logger(__name__)


@dataclass(frozen=True)
class Recipient:
    email: str
    first_name: str
    last_name: str = ""


class EmailProvider(ABC):
    @abstractmethod
    def send(self, *, to: str, subject: str, html: str, text: str) -> None: ...


class ConsoleEmailProvider(EmailProvider):
    def send(self, *, to: str, subject: str, html: str, text: str) -> None:
        logger.info(
            "email (console provider — not actually sent)",
            extra={"to": to, "subject": subject, "text_preview": text[:280]},
        )


class ResendEmailProvider(EmailProvider):
    def __init__(self, api_key: str) -> None:
        import resend

        resend.api_key = api_key
        self._resend = resend

    def send(self, *, to: str, subject: str, html: str, text: str) -> None:
        try:
            result = self._resend.Emails.send(
                {
                    "from": settings.email_from,
                    "to": [to],
                    "subject": subject,
                    "html": html,
                    "text": text,
                }
            )
            logger.info(
                "email sent", extra={"provider": "resend", "to": to, "id": result.get("id")}
            )
        except Exception:
            logger.exception("email delivery failed", extra={"to": to, "subject": subject})


_provider: EmailProvider | None = None


def get_email_provider() -> EmailProvider:
    global _provider
    if _provider is None:
        _provider = (
            ResendEmailProvider(settings.resend_api_key)
            if settings.resend_api_key
            else ConsoleEmailProvider()
        )
    return _provider


def reset_email_cache() -> None:
    """Test hook."""
    global _provider
    _provider = None


def send_new_lead_emails(*, prospect: Recipient, lead_id: str) -> None:
    """Notify the prospect and the internal attorney. Never raises."""
    provider = get_email_provider()

    confirmation = messages.prospect_confirmation(first_name=prospect.first_name)
    provider.send(
        to=prospect.email,
        subject=confirmation.subject,
        html=confirmation.html,
        text=confirmation.text,
    )

    dashboard_url = f"{settings.frontend_base_url}/leads/{lead_id}"
    notice = messages.attorney_notification(
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        email=prospect.email,
        lead_id=lead_id,
        dashboard_url=dashboard_url,
    )
    provider.send(
        to=settings.attorney_notification_email,
        subject=notice.subject,
        html=notice.html,
        text=notice.text,
    )
