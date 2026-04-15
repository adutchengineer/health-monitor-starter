"""Step 6: CPU Validation

Tests for the validator module — CPU-intensive payload validation
using ProcessPoolExecutor.
"""

import pytest


class TestValidator:
    def test_validate_valid_payload(self):
        """validate_payload should return valid=True for a correct payload."""
        from health_monitor.validator import validate_payload

        payload = '{"status": "ok", "version": "1.0"}'
        result = validate_payload(payload)
        assert result["valid"] is True

    def test_validate_invalid_json(self):
        """validate_payload should return valid=False for malformed JSON."""
        from health_monitor.validator import validate_payload

        result = validate_payload("{not valid json}")
        assert result["valid"] is False

    def test_validate_checksum(self):
        """validate_payload should verify checksums when provided."""
        from health_monitor.validator import validate_payload

        import hashlib
        import json

        data = json.dumps({"status": "ok"})
        checksum = hashlib.sha256(data.encode()).hexdigest()
        result = validate_payload(data, expected_checksum=checksum)
        assert result["valid"] is True

    def test_validate_bad_checksum(self):
        """validate_payload should fail on checksum mismatch."""
        from health_monitor.validator import validate_payload

        result = validate_payload('{"status": "ok"}', expected_checksum="bad")
        assert result["valid"] is False


class TestProcessPoolValidation:
    def test_batch_validate_uses_processes(self):
        """batch_validate should use ProcessPoolExecutor for large payloads."""
        from health_monitor.validator import batch_validate

        payloads = ['{"status": "ok"}'] * 10
        results = batch_validate(payloads)
        assert len(results) == 10
        assert all(r["valid"] for r in results)
