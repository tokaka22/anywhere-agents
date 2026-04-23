"""Tests for guard.py banner-gate diagnostics.

Covers the ack-file shapes that have historically caused Claude/Codex to
loop on the "Session banner not yet emitted" deny: the original message
quoted the expected JSON body with single quotes, and `_read_ts` returned
0 for every parse failure, so the agent never learned *why* the retry
was still failing. The checks below guard against regressions in the
diagnostic hint that now rides along on the deny message.

Run:  python3 scripts/test_guard_banner.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
import guard  # noqa: E402


def _make_consumer_root(tmp):
    cfg = os.path.join(tmp, ".agent-config")
    os.makedirs(cfg, exist_ok=True)
    with open(os.path.join(cfg, "bootstrap.sh"), "w") as f:
        f.write("#!/bin/sh\n")
    return tmp


def _write(root, name, content):
    path = os.path.join(root, ".agent-config", name)
    with open(path, "w") as f:
        f.write(content)
    return path


EVENT_TS = 1776934841.133697


class BannerGateTests(unittest.TestCase):
    def setUp(self):
        self._orig_cwd = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        self.root = _make_consumer_root(self._tmp.name)
        os.chdir(self.root)
        _write(self.root, "session-event.json", json.dumps({"ts": EVENT_TS}))

    def tearDown(self):
        os.chdir(self._orig_cwd)
        self._tmp.cleanup()

    def _check(self, ack=None):
        if ack is not None:
            _write(self.root, "banner-emitted.json", ack)
        return guard.check_banner_emission("Bash", {"command": "ls"})

    def test_valid_ack_passes(self):
        msg = self._check(ack=json.dumps({"ts": EVENT_TS}))
        self.assertIsNone(msg)

    def test_missing_ack_denies_without_note(self):
        msg = self._check(ack=None)
        self.assertIsNotNone(msg)
        self.assertIn("Session banner not yet emitted", msg)
        self.assertNotIn("NOTE:", msg)
        self.assertIn(f'{{"ts": {EVENT_TS}}}', msg)

    def test_quoted_body_denies_with_note(self):
        # Agent literally copied the single quotes from the old deny message.
        msg = self._check(ack=f"'{json.dumps({'ts': EVENT_TS})}'")
        self.assertIsNotNone(msg)
        self.assertIn("NOTE:", msg)
        self.assertIn("not valid JSON", msg)
        self.assertIn("single quotes", msg)

    def test_bare_number_denies_with_note(self):
        msg = self._check(ack=str(EVENT_TS))
        self.assertIsNotNone(msg)
        self.assertIn("NOTE:", msg)
        # Bare number parses as JSON but is not a dict.
        self.assertIn("malformed", msg)

    def test_wrong_key_denies_with_note(self):
        msg = self._check(ack=json.dumps({"timestamp": EVENT_TS}))
        self.assertIsNotNone(msg)
        self.assertIn("NOTE:", msg)
        self.assertIn("malformed", msg)

    def test_integer_ts_denies_without_note(self):
        # Valid shape but precision-stripped — deny triggers on staleness,
        # no structural note needed (agent just needs to re-write with full
        # precision from the deny body).
        msg = self._check(ack=json.dumps({"ts": int(EVENT_TS)}))
        self.assertIsNotNone(msg)
        self.assertNotIn("NOTE:", msg)

    def test_read_exempt(self):
        # Read is on the exempt list — gate must never fire for it.
        msg = guard.check_banner_emission("Read", {"file_path": "foo.txt"})
        self.assertIsNone(msg)


if __name__ == "__main__":
    unittest.main()
