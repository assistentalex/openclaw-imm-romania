#!/usr/bin/env python3
"""Render a GitHub checker digest JSON to Outlook-friendly HTML.

Reads JSON from stdin and prints HTML to stdout.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from html import escape
from typing import Any

BG = "#f4f6f8"
CARD = "#ffffff"
BORDER = "#d9e0e7"
TEXT = "#1f2937"
MUTED = "#64748b"
DARK = "#0f172a"
ACCENT = "#0ea5e9"
SUCCESS_BG = "#ecfdf5"
SUCCESS_TEXT = "#166534"
INFO_BG = "#eff6ff"
INFO_TEXT = "#1d4ed8"
WARN_BG = "#fff7ed"
WARN_TEXT = "#9a3412"
ERROR_BG = "#fef2f2"
ERROR_TEXT = "#b91c1c"
TABLE_HEAD = "#eaf2f8"
TABLE_ROW = "#f8fafc"


def _load_digest() -> dict[str, Any]:
    raw = sys.stdin.read()
    return json.loads(raw)


def _esc(value: Any) -> str:
    return escape(str(value if value is not None else ""), quote=True)


def _status_colors(status: str) -> tuple[str, str, str]:
    if status == "updated":
        return ("Updated", SUCCESS_BG, SUCCESS_TEXT)
    if status == "first_seen":
        return ("First seen", INFO_BG, INFO_TEXT)
    if status == "error":
        return ("Error", ERROR_BG, ERROR_TEXT)
    return ("Unchanged", TABLE_ROW, MUTED)


def _published_label(value: str | None) -> str:
    if not value:
        return "—"
    return _esc(value.replace("T", " ").replace("Z", " UTC"))


def _summary_card(label: str, value: Any, bg: str, fg: str) -> str:
    return (
        f'<td width="33.33%" valign="top" style="padding:0 8px 0 0;">'
        f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" '
        f'style="border-collapse:collapse;background:{bg};border:1px solid {BORDER};">'
        f'<tr><td style="padding:14px 16px;">'
        f'<div style="font-size:12px;line-height:18px;color:{fg};text-transform:uppercase;letter-spacing:0.04em;">{_esc(label)}</div>'
        f'<div style="font-size:28px;line-height:32px;font-weight:bold;color:{fg};margin-top:4px;">{_esc(value)}</div>'
        f'</td></tr></table></td>'
    )


def _render_highlights(results: list[dict[str, Any]]) -> str:
    items = [item for item in results if item.get("status") in {"updated", "first_seen", "error"}]
    if not items:
        return (
            '<tr><td style="padding:0 0 18px 0;">'
            '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" '
            f'style="border-collapse:collapse;background:{CARD};border:1px solid {BORDER};">'
            '<tr><td style="padding:16px 18px;">'
            f'<div style="font-size:18px;line-height:24px;font-weight:bold;color:{DARK};margin-bottom:8px;">Highlights</div>'
            f'<div style="font-size:14px;line-height:22px;color:{MUTED};">No new releases or errors this cycle. All tracked repositories are stable.</div>'
            '</td></tr></table></td></tr>'
        )

    rows = []
    for item in items:
        status = str(item.get("status") or "unchanged")
        repo = _esc(item.get("repo"))
        latest = _esc(item.get("latest_tag") or "—")
        previous = _esc(item.get("previous_tag") or "—")
        link = _esc(item.get("html_url") or "")
        error = _esc(item.get("error") or "")
        desc = _esc(item.get("description") or "")
        label, bg, fg = _status_colors(status)

        if status == "updated":
            summary = f'{previous} → {latest}'
        elif status == "first_seen":
            summary = f'First observed at {latest}'
        elif status == "error":
            summary = error or 'Unknown error'
        else:
            summary = latest

        link_html = f' &nbsp;·&nbsp; <a href="{link}" style="color:{ACCENT};text-decoration:none;">View release</a>' if link else ''
        rows.append(
            '<tr><td style="padding:0 0 10px 0;">'
            f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse:collapse;background:{CARD};border:1px solid {BORDER};">'
            '<tr>'
            f'<td valign="top" style="padding:14px 16px;">'
            f'<div style="font-size:15px;line-height:22px;font-weight:bold;color:{DARK};">{repo}</div>'
            f'<div style="font-size:13px;line-height:20px;color:{TEXT};margin-top:4px;">{summary}{link_html}</div>'
            f'{f"<div style=\"font-size:12px;color:{MUTED};margin-top:6px;\">{desc}</div>" if desc else ""}'
            '</td>'
            f'<td width="110" valign="top" align="right" style="padding:14px 16px;">'
            f'<span style="display:inline-block;padding:4px 10px;border:1px solid {bg};background:{bg};color:{fg};font-size:12px;line-height:16px;font-weight:bold;">{_esc(label)}</span>'
            '</td>'
            '</tr></table></td></tr>'
        )

    return (
        '<tr><td style="padding:0 0 18px 0;">'
        f'<div style="font-size:18px;line-height:24px;font-weight:bold;color:{DARK};margin-bottom:10px;">Highlights</div>'
        + ''.join(rows)
        + '</td></tr>'
    )


def _render_table(results: list[dict[str, Any]]) -> str:
    if not results:
        return (
            '<tr><td style="padding:0 0 18px 0;">'
            f'<div style="font-size:18px;line-height:24px;font-weight:bold;color:{DARK};margin-bottom:10px;">Repository Status</div>'
            f'<div style="font-size:14px;line-height:22px;color:{MUTED};">No tracked repositories yet.</div>'
            '</td></tr>'
        )

    rows = []
    for item in results:
        repo = _esc(item.get("repo"))
        latest = _esc(item.get("latest_tag") or "—")
        # compute days since / avg
        days_since = item.get("days_since_last_release")
        avg = item.get("avg_release_interval_days")
        if days_since is not None and avg is not None:
            days_html = f'{days_since} / {avg}'
        elif days_since is not None:
            days_html = f'{days_since} / -'
        elif avg is not None:
            days_html = f'- / {avg}'
        else:
            days_html = ' - '
        label, bg, fg = _status_colors(str(item.get("status") or "unchanged"))
        link = _esc(item.get("html_url") or "")
        repo_html = f'<a href="{link}" style="color:{ACCENT};text-decoration:none;">{repo}</a>' if link else repo
        desc = item.get("description") or ''
        desc_html = f'<div style="font-size:12px;color:{MUTED};margin-top:6px;">{_esc(desc)}</div>' if desc else ''
        rows.append(
            '<tr>'
            f'<td style="padding:10px 12px;border-top:1px solid {BORDER};font-size:13px;line-height:20px;color:{TEXT};">{repo_html}{desc_html}</td>'
            f'<td style="padding:10px 12px;border-top:1px solid {BORDER};font-size:13px;line-height:20px;color:{TEXT};">{latest}</td>'
            f'<td style="padding:10px 12px;border-top:1px solid {BORDER};font-size:13px;line-height:20px;color:{TEXT};">{_esc(days_html)}</td>'
            f'<td style="padding:10px 12px;border-top:1px solid {BORDER};font-size:13px;line-height:20px;"><span style="display:inline-block;padding:3px 8px;background:{bg};color:{fg};font-weight:bold;">{_esc(label)}</span></td>'
            '</tr>'
        )

    return (
        '<tr><td style="padding:0 0 18px 0;">'
        f'<div style="font-size:18px;line-height:24px;font-weight:bold;color:{DARK};margin-bottom:10px;">Repository Status</div>'
        f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse:collapse;background:{CARD};border:1px solid {BORDER};">'
        '<tr>'
        f'<td style="padding:10px 12px;background:{TABLE_HEAD};font-size:12px;line-height:18px;font-weight:bold;color:{DARK};text-transform:uppercase;">Repository</td>'
        f'<td style="padding:10px 12px;background:{TABLE_HEAD};font-size:12px;line-height:18px;font-weight:bold;color:{DARK};text-transform:uppercase;">Version</td>'
        f'<td style="padding:10px 12px;background:{TABLE_HEAD};font-size:12px;line-height:18px;font-weight:bold;color:{DARK};text-transform:uppercase;">Since / Avg (days)</td>'
        f'<td style="padding:10px 12px;background:{TABLE_HEAD};font-size:12px;line-height:18px;font-weight:bold;color:{DARK};text-transform:uppercase;">Status</td>'
        '</tr>'
        + ''.join(rows)
        + '</table></td></tr>'
    )


def render_html(data: dict[str, Any]) -> str:
    subject = _esc(data.get("subject") or "GitHub Releases")
    results = list(data.get("results") or [])
    updates = int(data.get("updates") or 0)
    failures = int(data.get("failures") or 0)
    monitored = len(results)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    intro = (
        "New releases or first-seen repositories were detected in the latest monitoring cycle."
        if any(item.get("status") in {"updated", "first_seen"} for item in results)
        else "No new releases were detected in the latest monitoring cycle."
    )

    parts = [
        '<html><body style="margin:0;padding:0;background:%s;font-family:Arial,Helvetica,sans-serif;color:%s;">' % (BG, TEXT),
        '<table role="presentation" width="100%%" cellspacing="0" cellpadding="0" border="0" style="background:%s;">' % BG,
        '<tr><td align="center" style="padding:24px;">',
        '<table role="presentation" width="760" cellspacing="0" cellpadding="0" border="0" style="width:760px;max-width:760px;background:%s;border:1px solid %s;">' % (CARD, BORDER),
        '<tr><td style="background:%s;padding:22px 28px;color:#ffffff;border-bottom:4px solid %s;">' % (DARK, ACCENT),
        '<table role="presentation" width="100%%" cellspacing="0" cellpadding="0" border="0" style="border-collapse:collapse;">',
        '<tr>',
        '<td valign="middle" width="78" style="padding:0 14px 0 0;">',
        f'<div style="width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,{ACCENT},{INFO_TEXT});text-align:center;line-height:64px;font-size:18px;font-weight:700;color:#ffffff;">AI</div>',
        '</td>',
        '<td valign="middle" style="padding:0;">',
        '<div style="font-size:12px;line-height:18px;letter-spacing:0.14em;text-transform:uppercase;opacity:0.88;">Firma de AI</div>',
        '<div style="font-size:18px;line-height:24px;font-weight:700;margin-top:4px;opacity:0.98;">powered by <a href="https://firmade.it" style="color:#ffffff;text-decoration:none;">Firma de IT</a></div>',
        '<div style="font-size:28px;line-height:34px;font-weight:bold;margin-top:8px;">GitHub Releases Digest</div>',
        '<div style="font-size:15px;line-height:22px;font-weight:600;opacity:0.96;margin-top:8px;">%s</div>' % _esc(subject),
        '<div style="font-size:14px;line-height:22px;opacity:0.90;margin-top:10px;">%s</div>' % _esc(intro),
        '<div style="font-size:12px;line-height:18px;opacity:0.78;margin-top:12px;">Generated: %s • Inteligență utilă pentru echipe românești</div>' % _esc(timestamp),
        '</td>',
        '</tr></table>',
        '</td></tr>',
        '<tr><td style="padding:24px 28px;">',
        '<table role="presentation" width="100%%" cellspacing="0" cellpadding="0" border="0" style="border-collapse:collapse;margin-bottom:18px;">',
        '<tr>',
        _summary_card('Tracked repos', monitored, CARD, DARK),
        _summary_card('Updates', updates, SUCCESS_BG if updates else CARD, SUCCESS_TEXT if updates else DARK),
        _summary_card('Failures', failures, ERROR_BG if failures else CARD, ERROR_TEXT if failures else DARK),
        '</tr></table>',
        _render_highlights(results),
        _render_table(results),
        '<tr><td style="padding:0;">',
        '<div style="font-size:12px;line-height:18px;color:%s;">Next check: scheduled by cron.</div>' % MUTED,
        '</td></tr>',
        '</td></tr>',
        '<tr><td style="background:#eef2f7;padding:16px 28px;font-size:12px;line-height:18px;color:%s;">'
        '<div style="margin:0 0 6px 0;">Generated by IMM-Romania MSP GitHub checker · <a href="https://github.com/assistentalex/openclaw-imm-romania" style="color:%s;text-decoration:none;font-weight:600;">public repo</a></div>'
        '<div style="margin:0;">Firma de AI is powered by <a href="https://firmade.it" style="color:%s;text-decoration:none;font-weight:600;">Firma de IT</a> · <a href="https://www.firmade.ai" style="color:%s;text-decoration:none;font-weight:600;">www.FirmaDe.AI</a></div>'
        '</td></tr>' % (MUTED, ACCENT, ACCENT, ACCENT),
        '</table></td></tr></table></body></html>',
    ]
    return ''.join(parts)


def main() -> int:
    try:
        data = _load_digest()
    except Exception:
        print('<p>Invalid digest</p>')
        return 1

    print(render_html(data))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
