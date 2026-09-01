"""Email content builders.

Plain Python string templates (no Jinja dependency) so payloads are easy to
unit-test and diff. Each builder returns ``(subject, html, text)``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RenderedEmail:
    subject: str
    html: str
    text: str


_WRAPPER = """\
<!doctype html>
<html>
  <body style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#1a1a2e;line-height:1.6;max-width:560px;margin:0 auto;padding:24px">
    {body}
    <hr style="border:none;border-top:1px solid #e5e5ef;margin:32px 0 16px" />
    <p style="font-size:12px;color:#8a8aa3">ProjectAlma</p>
  </body>
</html>
"""


def _html(body: str) -> str:
    return _WRAPPER.format(body=body)


def prospect_confirmation(*, first_name: str) -> RenderedEmail:
    subject = "We received your submission"
    body = f"""
      <h2>Thanks, {first_name}.</h2>
      <p>We've received your information. A qualified attorney will review your
      profile and contact you by email with a strategic plan for your visa
      process.</p>
      <p>No action is needed from you right now.</p>
    """
    text = (
        f"Thanks, {first_name}.\n\n"
        "We've received your information. A qualified attorney will review your "
        "profile and contact you by email with a strategic plan for your visa "
        "process.\n\n"
        "No action is needed from you right now."
    )
    return RenderedEmail(subject=subject, html=_html(body), text=text)


def attorney_notification(
    *, first_name: str, last_name: str, email: str, lead_id: str, dashboard_url: str
) -> RenderedEmail:
    subject = f"New lead: {first_name} {last_name}"
    body = f"""
      <h2>New lead submitted</h2>
      <table style="border-collapse:collapse">
        <tr><td style="padding:4px 12px 4px 0;color:#8a8aa3">Name</td><td>{first_name} {last_name}</td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#8a8aa3">Email</td><td>{email}</td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#8a8aa3">Lead ID</td><td>{lead_id}</td></tr>
      </table>
      <p style="margin-top:24px">
        <a href="{dashboard_url}" style="background:#0b756e;color:#fff;padding:10px 18px;border-radius:6px;text-decoration:none">
          Open in dashboard
        </a>
      </p>
    """
    text = (
        "New lead submitted\n\n"
        f"Name:  {first_name} {last_name}\n"
        f"Email: {email}\n"
        f"Lead ID: {lead_id}\n\n"
        f"Open in dashboard: {dashboard_url}\n"
    )
    return RenderedEmail(subject=subject, html=_html(body), text=text)
