#!/usr/bin/env python3
"""Tests for render_digest.py"""

import json
import subprocess
import sys
from pathlib import Path

TEST_DIGEST = {
    "subject": "Test Digest",
    "results": [
        {"repo": "owner/repo", "status": "first_seen", "latest_tag": "v1.0.0", "html_url": "https://example.com"}
    ],
    "updates": 1,
    "failures": 0,
}


def test_render_digest_stdout(tmp_path):
    p = subprocess.run([
        sys.executable,
        str(Path(__file__).resolve().parents[1] / 'modules' / 'msp' / 'render_digest.py')
    ], input=json.dumps(TEST_DIGEST).encode('utf-8'), stdout=subprocess.PIPE)
    out = p.stdout.decode('utf-8')
    assert 'GitHub Releases' in out or 'Test Digest' in out
    assert 'owner/repo' in out


if __name__ == '__main__':
    test_render_digest_stdout(Path('.'))
    print('ok')
