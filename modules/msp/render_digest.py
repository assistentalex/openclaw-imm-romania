#!/usr/bin/env python3
"""Render a GitHub checker digest JSON to Outlook-friendly HTML.

Reads JSON from stdin and prints HTML to stdout.
"""
import json
import sys
from datetime import datetime

RAW = sys.stdin.read()
try:
    data = json.loads(RAW)
except Exception:
    print('<p>Invalid digest</p>')
    sys.exit(1)

subject = data.get('subject','GitHub Releases')
results = data.get('results', [])
updates = data.get('updates', 0)
failures = data.get('failures', 0)

html_lines = []
html_lines.append('<div style="font-family:Arial,Helvetica,sans-serif;color:#1f2937;">')
html_lines.append(f'<h2 style="margin:0;padding:0;">{subject}</h2>')
html_lines.append(f'<p style="color:#6b7280;margin:6px 0 14px 0;">Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</p>')
html_lines.append(f'<p style="margin:0 0 12px 0;"><strong>Updates:</strong> {updates} &nbsp;&nbsp; <strong>Failures:</strong> {failures}</p>')

if results:
    new_items = [it for it in results if it.get('status') in ('updated','first_seen')]
    if new_items:
        html_lines.append('<h3 style="margin:14px 0 6px 0;color:#0f172a;">New & Notable</h3>')
        html_lines.append('<ul style="margin:6px 0 12px 18px;">')
        for it in new_items:
            status = it.get('status')
            repo = it.get('repo')
            if status == 'updated':
                html_lines.append(f'<li><strong>{repo}</strong>: {it.get("previous_tag")} → {it.get("latest_tag")} — <a href="{it.get("html_url")}">releases</a></li>')
            else:
                html_lines.append(f'<li><strong>{repo}</strong>: first seen at {it.get("latest_tag")} — <a href="{it.get("html_url")}">releases</a></li>')
        html_lines.append('</ul>')
    html_lines.append('<h3 style="margin:8px 0 6px 0;color:#0f172a;">Repository Status</h3>')
    html_lines.append('<table cellspacing="0" cellpadding="6" border="0" style="border-collapse:collapse;width:100%;">')
    html_lines.append('<tr style="background:#f1f5f9;color:#0f172a;font-weight:600;"><td>Repository</td><td>Version</td><td>Published</td><td>Status</td></tr>')
    for it in results:
        repo = it.get('repo')
        latest = it.get('latest_tag') or ''
        published = it.get('published_at') or ''
        status = it.get('status') or ''
        html_lines.append(f'<tr style="border-top:1px solid #e6eef5;"><td><a href="{it.get("html_url")}" style="color:#0369a1;text-decoration:none;">{repo}</a></td><td>{latest}</td><td>{published}</td><td>{status}</td></tr>')
    html_lines.append('</table>')
else:
    html_lines.append('<p>No tracked repositories yet.</p>')

html_lines.append(f'<p style="margin-top:12px;color:#6b7280;font-size:12px;">Next check: scheduled by cron</p>')
html_lines.append('</div>')

print('\n'.join(html_lines))
